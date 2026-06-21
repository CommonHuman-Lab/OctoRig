# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_or_api_key, get_db, get_deployment_or_404
from app.core.exceptions import bad_request, conflict, forbidden_exception, not_found
from app.core.permissions import can_destroy_deployment, can_view_logs, is_privileged
from app.labs.registry import REGISTRY_BY_ID
from app.models.challenge import Challenge
from app.models.deployment import Deployment, DeploymentStatus
from app.models.lab_template import LabTemplate
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.deployment import DeploymentCreate, DeploymentResponse, DeploymentWithTemplate
from app.services import audit_service, lab_service
from app.services.challenge_rendering import render_access_info
from app.services.deployment_provisioning import prepare_deployment
from app.services.docker_runtime import docker_service

router = APIRouter(prefix="/deployments", tags=["deployments"])


def _get_membership(db: Session, user: User, team_id: Optional[int]) -> Optional[TeamMember]:
    if team_id is None:
        return None
    return (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.user_id == user.id)
        .first()
    )


def _to_response(d: Deployment, db: Session) -> DeploymentWithTemplate:
    template = db.get(LabTemplate, d.lab_template_id)
    user = db.get(User, d.started_by_id)
    team = db.get(Team, d.team_id) if d.team_id else None
    base = DeploymentResponse.model_validate(d).model_dump()
    # Legacy rows predate per-deployment network isolation and have no access_info
    if not base.get("access_info") and template is not None:
        base["access_info"] = render_access_info(template.access_info or [])
    return DeploymentWithTemplate(
        **base,
        lab_name=template.name if template else "Unknown",
        lab_slug=template.slug if template else "",
        lab_category=template.category if template else "",
        started_by_username=user.username if user else "unknown",
        team_name=team.name if team else None,
    )


def _visible_to_user(d: Deployment, user: User, db: Session) -> bool:
    """True if `user` should be able to see this deployment."""
    if is_privileged(user, db):
        return True
    if d.started_by_id == user.id:
        return True
    if d.visibility.value == "public":
        return True
    if d.team_id and d.visibility.value == "team":
        member = _get_membership(db, user, d.team_id)
        return member is not None
    return False


@router.get("/", response_model=list[DeploymentWithTemplate])
def list_deployments(
    status: Optional[str] = Query(None),
    team_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
) -> list[DeploymentWithTemplate]:
    q = db.query(Deployment)

    if not is_privileged(current_user, db):
        member_team_ids = [
            m.team_id
            for m in db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
        ]
        from sqlalchemy import or_
        q = q.filter(
            or_(
                Deployment.started_by_id == current_user.id,
                Deployment.visibility == "public",
                (Deployment.team_id.in_(member_team_ids) if member_team_ids else False),
            )
        )

    if status:
        q = q.filter(Deployment.status == status)
    if team_id is not None:
        q = q.filter(Deployment.team_id == team_id)

    deployments = q.order_by(Deployment.created_at.desc()).offset(offset).limit(limit).all()
    return [_to_response(d, db) for d in deployments]


@router.get("/instance", response_model=Optional[DeploymentWithTemplate])
def get_my_instance(
    challenge_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
) -> Optional[DeploymentWithTemplate]:
    """Return the caller's active instance for a challenge, or null."""
    d = (
        db.query(Deployment)
        .filter(
            Deployment.challenge_id == challenge_id,
            Deployment.instance_for_user_id == current_user.id,
            Deployment.status.in_([DeploymentStatus.STARTING, DeploymentStatus.RUNNING]),
        )
        .first()
    )
    if d is None:
        return None
    return _to_response(d, db)


@router.get("/{deployment_id}", response_model=DeploymentWithTemplate)
def get_deployment(
    d: Deployment = Depends(get_deployment_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
) -> DeploymentWithTemplate:
    if not _visible_to_user(d, current_user, db):
        raise not_found("Deployment")  # don't leak existence
    return _to_response(d, db)


@router.post("/", response_model=DeploymentWithTemplate, status_code=202)
def create_deployment(
    payload: DeploymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
) -> DeploymentWithTemplate:
    # Resolve lab template id — challenge_id takes precedence when provided
    lab_template_id = payload.lab_template_id
    challenge_id = payload.challenge_id
    instance_for_user_id = None
    auto_destroy_at = None

    if challenge_id is not None:
        ch = db.get(Challenge, challenge_id)
        if ch is None:
            raise not_found("Challenge")
        lab_template_id = ch.lab_template_id
        if lab_template_id is None:
            raise bad_request("Challenge has no associated lab template")
        instance_for_user_id = current_user.id
        auto_destroy_at = datetime.now(timezone.utc) + timedelta(hours=max(1, min(8, payload.ttl_hours)))

    # Locked for the transaction so concurrent deployment requests serialize past the conflict check
    template = (
        db.query(LabTemplate)
        .filter(LabTemplate.id == lab_template_id)
        .with_for_update()
        .first()
    )
    if template is None:
        raise not_found("Lab template")

    if payload.team_id is not None:
        team = db.get(Team, payload.team_id)
        if team is None:
            raise not_found("Team")
        membership = _get_membership(db, current_user, payload.team_id)
        if membership is None and not is_privileged(current_user, db):
            raise forbidden_exception

    lab_def = REGISTRY_BY_ID.get(template.id)
    if lab_def is None:
        raise bad_request("Lab definition missing from registry")

    # Conflict check is per-user (challenges/personal labs) or per-team (team labs);
    # race-free under the SELECT FOR UPDATE above, backed by the DB partial unique indexes.
    if challenge_id is not None:
        existing = (
            db.query(Deployment)
            .filter(
                Deployment.challenge_id == challenge_id,
                Deployment.instance_for_user_id == current_user.id,
                Deployment.status.in_([DeploymentStatus.STARTING, DeploymentStatus.RUNNING]),
            )
            .first()
        )
        if existing is not None:
            raise conflict(f"You already have an active instance for this challenge (id={existing.id})")
    elif payload.team_id is not None:
        existing = lab_service.get_active_deployment(db, template.id, team_id=payload.team_id)
        if existing is not None:
            raise conflict(f"Your team already has an active deployment of '{template.name}' (id={existing.id})")
    else:
        existing = lab_service.get_active_deployment(db, template.id, started_by_id=current_user.id)
        if existing is not None:
            raise conflict(f"You already have an active deployment of '{template.name}' (id={existing.id})")

    deployment = prepare_deployment(
        db,
        template,
        lab_def,
        started_by_id=current_user.id,
        team_id=payload.team_id,
        challenge_id=challenge_id,
        instance_for_user_id=instance_for_user_id,
        auto_destroy_at=auto_destroy_at,
        visibility=payload.visibility,
    )
    db.commit()
    db.refresh(deployment)

    background_tasks.add_task(lab_service.start_lab, deployment.id, current_user.id)
    return _to_response(deployment, db)


@router.delete("/{deployment_id}", response_model=DeploymentWithTemplate, status_code=202)
def destroy_deployment(
    background_tasks: BackgroundTasks,
    d: Deployment = Depends(get_deployment_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
) -> DeploymentWithTemplate:
    membership = _get_membership(db, current_user, d.team_id)
    if not can_destroy_deployment(current_user, db, d, membership):
        raise forbidden_exception

    if d.status not in (DeploymentStatus.RUNNING, DeploymentStatus.ERROR):
        raise bad_request(f"Deployment is {d.status.value} — can only stop running or errored deployments")

    d.status = DeploymentStatus.STOPPING
    db.commit()

    background_tasks.add_task(lab_service.stop_lab, d.id, current_user.id)
    return _to_response(d, db)


@router.post("/{deployment_id}/start", response_model=DeploymentWithTemplate, status_code=202)
def start_deployment(
    background_tasks: BackgroundTasks,
    d: Deployment = Depends(get_deployment_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
) -> DeploymentWithTemplate:
    membership = _get_membership(db, current_user, d.team_id)
    if not can_destroy_deployment(current_user, db, d, membership):
        raise forbidden_exception

    if d.status not in (DeploymentStatus.STOPPED, DeploymentStatus.ERROR):
        raise bad_request(f"Deployment is {d.status.value} — can only start stopped or errored deployments")

    d.status = DeploymentStatus.STARTING
    d.error_message = None
    db.commit()

    background_tasks.add_task(lab_service.start_lab, d.id, current_user.id)
    return _to_response(d, db)


@router.delete("/{deployment_id}/purge", status_code=204)
def purge_deployment(
    d: Deployment = Depends(get_deployment_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
) -> None:
    membership = _get_membership(db, current_user, d.team_id)
    if not can_destroy_deployment(current_user, db, d, membership):
        raise forbidden_exception

    if d.status not in (DeploymentStatus.STOPPED, DeploymentStatus.ERROR):
        raise bad_request(f"Deployment is {d.status.value} — can only remove stopped or errored deployments")

    lab_service.purge_deployment(db, d.id, current_user.id)


@router.patch("/{deployment_id}/visibility", response_model=DeploymentWithTemplate)
def set_visibility(
    visibility: str = Query(..., pattern="^(private|team|public)$"),
    d: Deployment = Depends(get_deployment_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
) -> DeploymentWithTemplate:
    from app.models.deployment import DeploymentVisibility
    membership = _get_membership(db, current_user, d.team_id)
    if not can_destroy_deployment(current_user, db, d, membership):  # same permission as mutate
        raise forbidden_exception
    d.visibility = DeploymentVisibility(visibility)
    db.commit()
    return _to_response(d, db)


@router.post("/{deployment_id}/reset", response_model=DeploymentWithTemplate, status_code=202)
def reset_deployment(
    background_tasks: BackgroundTasks,
    d: Deployment = Depends(get_deployment_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
) -> DeploymentWithTemplate:
    membership = _get_membership(db, current_user, d.team_id)
    if not can_destroy_deployment(current_user, db, d, membership):
        raise forbidden_exception

    template = db.get(LabTemplate, d.lab_template_id)
    if template is None or template.category != "firerange":
        raise bad_request("Reset is only available for fire-range labs")

    background_tasks.add_task(lab_service.reset_lab, d.id, current_user.id)
    return _to_response(d, db)


@router.websocket("/{deployment_id}/logs")
async def stream_logs(
    websocket: WebSocket,
    deployment_id: int,
    container: str = Query("app", description="Container role to stream logs from"),
    tail: int = Query(100, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> None:
    # Accept the connection first so we can send close codes back to the client.
    await websocket.accept()

    # Auth via first message avoids placing JWT in the URL, where every proxy/LB logs it
    import asyncio
    import json as _json
    from jose import JWTError
    from app.core.security import decode_access_token

    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
        token = _json.loads(raw).get("token", "")
        user_id = decode_access_token(token)
        current_user = db.get(User, int(user_id))
        if current_user is None or not current_user.is_active:
            await websocket.close(code=4001)
            return
    except (asyncio.TimeoutError, JWTError, Exception):
        await websocket.close(code=4001)
        return

    d = db.get(Deployment, deployment_id)
    if d is None:
        await websocket.close(code=4004)
        return

    membership = _get_membership(db, current_user, d.team_id)
    if not can_view_logs(current_user, db, d, membership):
        await websocket.close(code=4003)
        return

    template = db.get(LabTemplate, d.lab_template_id)
    container_name = _resolve_container_name(d, template, container)

    try:
        async for line in docker_service.stream_logs(container_name, tail=tail):
            await websocket.send_text(line)
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()


def _resolve_container_name(deployment: Deployment, template: Optional[LabTemplate], role: str) -> str:
    """Pick this deployment's own container name for `role` — never the
    template's static name, which no longer matches any running container
    now that containers are named per-deployment (see prepare_deployment())."""
    dep_names = deployment.container_names
    if not dep_names:
        return template.container_names[0] if template else ""
    if len(dep_names) == 1 or template is None:
        return dep_names[0]
    # template/deployment container_names are generated 1:1 in the same order
    for i, name in enumerate(template.container_names):
        if name.endswith(f"-{role}") and i < len(dep_names):
            return dep_names[i]
    return dep_names[0]
