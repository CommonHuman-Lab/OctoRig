# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime, timezone

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_client_ip, get_current_user_or_api_key
from app.core.exceptions import bad_request, forbidden_exception, not_found
from app.core.permissions import is_privileged
from app.database import get_db
from app.models.scheduled_action import ScheduledAction, ScheduledActionStatus, ScheduledActionType
from app.models.user import User
from app.schemas.scheduled_action import ScheduledActionCreate, ScheduledActionResponse
from app.services import audit_service

router = APIRouter(prefix="/schedule", tags=["scheduler"])


@router.get("/", response_model=list[ScheduledActionResponse])
def list_scheduled(
    status: ScheduledActionStatus | None = Query(None),
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
) -> list[ScheduledActionResponse]:
    q = db.query(ScheduledAction)
    if not is_privileged(current_user, db):
        q = q.filter(ScheduledAction.user_id == current_user.id)
    if status:
        q = q.filter(ScheduledAction.status == status)
    actions = q.order_by(ScheduledAction.scheduled_at).all()
    return [ScheduledActionResponse.model_validate(a) for a in actions]


@router.post("/", response_model=ScheduledActionResponse, status_code=201)
def create_scheduled(
    payload: ScheduledActionCreate,
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> ScheduledActionResponse:
    if payload.scheduled_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        raise bad_request("scheduled_at must be in the future")

    if payload.action == ScheduledActionType.DESTROY and payload.deployment_id:
        from app.models.deployment import Deployment
        from app.core.permissions import can_destroy_deployment
        from app.api.deployments import _get_membership

        d = db.get(Deployment, payload.deployment_id)
        if d is None:
            raise not_found("Deployment")
        membership = _get_membership(db, current_user, d.team_id)
        if not can_destroy_deployment(current_user, db, d, membership):
            raise forbidden_exception

    if payload.team_id is not None:
        from app.models.team import TeamMember
        member = (
            db.query(TeamMember)
            .filter(TeamMember.team_id == payload.team_id, TeamMember.user_id == current_user.id)
            .first()
        )
        if member is None and not is_privileged(current_user, db):
            raise forbidden_exception

    action = ScheduledAction(
        user_id=current_user.id,
        team_id=payload.team_id,
        lab_template_id=payload.lab_template_id,
        deployment_id=payload.deployment_id,
        action=payload.action,
        scheduled_at=payload.scheduled_at,
    )
    db.add(action)
    db.commit()
    db.refresh(action)

    audit_service.write_audit(
        db,
        action=audit_service.SCHEDULE_CREATED,
        user_id=current_user.id,
        team_id=payload.team_id,
        deployment_id=payload.deployment_id,
        detail={
            "action": payload.action.value,
            "scheduled_at": payload.scheduled_at.isoformat(),
        },
        ip=ip,
    )
    return ScheduledActionResponse.model_validate(action)


@router.delete("/{action_id}", status_code=204)
def cancel_scheduled(
    action_id: int,
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> None:
    action = db.get(ScheduledAction, action_id)
    if action is None:
        raise not_found("Scheduled action")
    if action.user_id != current_user.id and not is_privileged(current_user, db):
        raise forbidden_exception
    if action.status != ScheduledActionStatus.PENDING:
        raise bad_request(f"Cannot cancel action with status '{action.status.value}'")

    action.status = ScheduledActionStatus.CANCELLED
    db.commit()

    audit_service.write_audit(
        db,
        action=audit_service.SCHEDULE_CANCELLED,
        user_id=current_user.id,
        detail={"scheduled_action_id": action_id},
        ip=ip,
    )
