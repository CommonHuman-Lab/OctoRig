# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_client_ip, get_db, get_user_or_404, require_admin
from app.core.db_helpers import raise_if_exists
from app.core.exceptions import bad_request, conflict, not_found
from app.core.security import hash_password
from app.models.api_key import ApiKey
from app.models.assessment import AssessmentInvite, AssessmentReport
from app.models.audit_log import AuditLog
from app.models.badge import UserBadge
from app.models.challenge import ChallengeSubmission, HintUnlock
from app.models.ctf_event import EventRegistration
from app.models.deployment import Deployment, DeploymentStatus
from app.models.lab_template import LabTemplate
from app.models.notification import Notification
from app.models.rank import Rank
from app.models.refresh_token import RefreshToken
from app.models.scheduled_action import ScheduledAction, ScheduledActionStatus
from app.models.scoring import ScoreTransaction
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.admin import (
    AdminApiKeyResponse,
    AdminAuditLogResponse,
    AdminResetPassword,
    AdminTeamResponse,
    AdminUserCreate,
    AdminUserResponse,
    AdminUserUpdate,
    SiteSettingsResponse,
    SiteSettingsUpdate,
    SystemStats,
)
from app.services import api_key_service, audit_service, lab_service
from app.services.docker_runtime import docker_service
from app.services.settings_service import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=SystemStats)
def get_stats(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SystemStats:
    active_statuses = [DeploymentStatus.STARTING, DeploymentStatus.RUNNING]
    return SystemStats(
        user_count=db.query(User).count(),
        team_count=db.query(Team).filter(Team.is_personal.is_(False)).count(),
        active_deployments=db.query(Deployment).filter(Deployment.status.in_(active_statuses)).count(),
        total_deployments=db.query(Deployment).count(),
        api_key_count=db.query(ApiKey).filter(ApiKey.is_active.is_(True)).count(),
        pending_scheduled_actions=db.query(ScheduledAction)
            .filter(ScheduledAction.status == ScheduledActionStatus.PENDING)
            .count(),
    )


# ── Users ────────────────────────────────────────────────────────────────────

def _enrich_user(user: User, db: Session) -> AdminUserResponse:
    team_count = db.query(TeamMember).filter(TeamMember.user_id == user.id).count()
    deployment_count = db.query(Deployment).filter(Deployment.started_by_id == user.id).count()
    api_key_count = db.query(ApiKey).filter(ApiKey.user_id == user.id, ApiKey.is_active.is_(True)).count()
    return AdminUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_owner=user.is_owner,
        platform_roles=user.platform_roles or [],
        locked_until=user.locked_until,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        team_count=team_count,
        deployment_count=deployment_count,
        api_key_count=api_key_count,
    )


@router.get("/users/", response_model=list[AdminUserResponse])
def list_users(
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminUserResponse]:
    q = db.query(User)
    if search:
        like = f"%{search}%"
        q = q.filter((User.username.ilike(like)) | (User.email.ilike(like)))
    users = q.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    return [_enrich_user(u, db) for u in users]


@router.post("/users/", response_model=AdminUserResponse, status_code=201)
def create_user(
    payload: AdminUserCreate,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> AdminUserResponse:
    raise_if_exists(db, User, f"Username '{payload.username}' is already taken", username=payload.username)
    raise_if_exists(db, User, f"Email '{payload.email}' is already registered", email=payload.email)

    from app.models.role import PlatformRole

    valid_slugs = {r.slug for r in db.query(PlatformRole.slug).all()}
    invalid = set(payload.platform_roles) - valid_slugs
    if invalid:
        raise bad_request(f"Unknown role slugs: {sorted(invalid)}")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_active=True,
        platform_roles=payload.platform_roles,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    from app.services.team_service import ensure_personal_team
    ensure_personal_team(db, user)

    audit_service.write_audit(
        db, action=audit_service.ADMIN_USER_CREATED, user_id=actor.id,
        detail={"created_username": payload.username},
        ip=ip,
    )
    return _enrich_user(user, db)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user(
    user: User = Depends(get_user_or_404),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    return _enrich_user(user, db)


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_user(
    payload: AdminUserUpdate,
    user: User = Depends(get_user_or_404),
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> AdminUserResponse:
    if user.id == actor.id and payload.is_active is False:
        raise bad_request("Cannot deactivate your own account")
    if user.id == actor.id and payload.platform_roles is not None:
        raise bad_request("Cannot change your own roles")
    if user.is_owner and payload.is_active is False:
        raise bad_request("The owner account cannot be deactivated")
    if user.is_owner and payload.platform_roles is not None:
        raise bad_request("The owner's roles cannot be changed")
    if payload.is_active is False and "admin" in (user.platform_roles or []):
        other_active_admins = (
            db.query(User)
            .filter(User.id != user.id, User.is_active.is_(True))
            .all()
        )
        if not any("admin" in (u.platform_roles or []) for u in other_active_admins):
            raise bad_request("Cannot deactivate the last remaining admin")

    changes: dict = {}
    if payload.is_active is not None:
        user.is_active = payload.is_active
        changes["is_active"] = payload.is_active
    if payload.platform_roles is not None:
        from app.models.role import PlatformRole

        valid_slugs = {r.slug for r in db.query(PlatformRole.slug).all()}
        invalid = set(payload.platform_roles) - valid_slugs
        if invalid:
            raise bad_request(f"Unknown role slugs: {sorted(invalid)}")
        user.platform_roles = payload.platform_roles
        changes["platform_roles"] = payload.platform_roles
    if payload.unlock:
        from app.services.login_lockout_service import reset as reset_lockout

        reset_lockout(user)
        changes["unlocked"] = True

    db.commit()
    audit_service.write_audit(
        db, action=audit_service.ADMIN_ROLE_CHANGED, user_id=actor.id,
        detail={"target_user_id": user.id, "changes": changes},
        ip=ip,
    )
    return _enrich_user(user, db)


@router.post("/users/{user_id}/reset-password", status_code=204)
def reset_password(
    payload: AdminResetPassword,
    user: User = Depends(get_user_or_404),
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> None:
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    audit_service.write_audit(
        db, action="admin.password_reset", user_id=actor.id,
        detail={"target_user_id": user.id},
        ip=ip,
    )


@router.post("/users/{user_id}/reset-points", status_code=204)
def reset_user_points(
    user: User = Depends(get_user_or_404),
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> None:
    db.query(ScoreTransaction).filter(ScoreTransaction.user_id == user.id).delete()
    db.query(ChallengeSubmission).filter(ChallengeSubmission.user_id == user.id).delete()
    db.query(HintUnlock).filter(HintUnlock.user_id == user.id).delete()
    db.commit()
    audit_service.write_audit(
        db, action="admin.reset_points", user_id=actor.id,
        detail={"target_user_id": user.id},
        ip=ip,
    )


@router.post("/reset-db", status_code=204)
def reset_database(
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> None:
    """Wipe all user-generated activity, keeping accounts, teams, labs, challenges and assessment config."""
    # Child tables first (FK constraints)
    db.query(AssessmentReport).delete()
    db.query(AssessmentInvite).delete()
    db.query(ChallengeSubmission).delete()
    db.query(HintUnlock).delete()
    db.query(ScoreTransaction).delete()
    db.query(UserBadge).delete()
    db.query(EventRegistration).delete()
    db.query(Notification).delete()
    db.query(Deployment).delete()
    db.query(ScheduledAction).delete()
    db.query(RefreshToken).delete()
    db.query(AuditLog).delete()
    db.commit()
    audit_service.write_audit(
        db, action="admin.reset_db", user_id=actor.id,
        detail={"triggered_by": actor.username},
        ip=ip,
    )


# ── Teams ────────────────────────────────────────────────────────────────────

@router.get("/teams/", response_model=list[AdminTeamResponse])
def list_teams(
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminTeamResponse]:
    q = db.query(Team)
    if search:
        q = q.filter(Team.name.ilike(f"%{search}%"))
    teams = q.order_by(Team.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for team in teams:
        creator = db.get(User, team.created_by_id)
        member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
        deployment_count = db.query(Deployment).filter(Deployment.team_id == team.id).count()
        result.append(
            AdminTeamResponse(
                id=team.id,
                name=team.name,
                slug=team.slug,
                is_personal=team.is_personal,
                created_by_id=team.created_by_id,
                created_by_username=creator.username if creator else "unknown",
                member_count=member_count,
                deployment_count=deployment_count,
                created_at=team.created_at,
            )
        )
    return result


# ── Labs ─────────────────────────────────────────────────────────────────────

class AdminLabResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    category: str
    requires_privileged: bool
    is_active: bool
    exposed_ports: dict
    container_names: list[str]
    active_deployment_count: int
    total_deployment_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminLabUpdate(BaseModel):
    is_active: bool


def _enrich_admin_lab(template: LabTemplate, db: Session) -> AdminLabResponse:
    active_count = db.query(Deployment).filter(
        Deployment.lab_template_id == template.id,
        Deployment.status.in_([DeploymentStatus.STARTING, DeploymentStatus.RUNNING]),
    ).count()
    total_count = db.query(Deployment).filter(Deployment.lab_template_id == template.id).count()
    return AdminLabResponse(
        id=template.id,
        slug=template.slug,
        name=template.name,
        description=template.description,
        category=template.category,
        requires_privileged=template.requires_privileged,
        is_active=template.is_active,
        exposed_ports=template.exposed_ports,
        container_names=template.container_names,
        active_deployment_count=active_count,
        total_deployment_count=total_count,
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


@router.get("/labs/", response_model=list[AdminLabResponse])
def list_admin_labs(
    category: Optional[str] = Query(None),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminLabResponse]:
    q = db.query(LabTemplate)
    if category:
        q = q.filter(LabTemplate.category == category)
    templates = q.order_by(LabTemplate.id).all()
    return [_enrich_admin_lab(t, db) for t in templates]


@router.patch("/labs/{lab_id}", response_model=AdminLabResponse)
def update_admin_lab(
    lab_id: int,
    body: AdminLabUpdate,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> AdminLabResponse:
    template = db.get(LabTemplate, lab_id)
    if template is None:
        raise not_found("Lab")
    if template.is_active != body.is_active:
        template.is_active = body.is_active
        db.commit()
        db.refresh(template)
        audit_service.write_audit(
            db, action=audit_service.ADMIN_LAB_TOGGLED, user_id=actor.id,
            detail={"lab_id": lab_id, "lab_slug": template.slug, "is_active": body.is_active},
            ip=ip,
        )
    return _enrich_admin_lab(template, db)


# ── Deployments (all) ────────────────────────────────────────────────────────

@router.get("/deployments/", response_model=list[dict])
def list_all_deployments(
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    team_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[dict]:
    from app.api.deployments import _to_response
    q = db.query(Deployment)
    if status:
        q = q.filter(Deployment.status == status)
    if user_id:
        q = q.filter(Deployment.started_by_id == user_id)
    if team_id:
        q = q.filter(Deployment.team_id == team_id)
    deployments = q.order_by(Deployment.created_at.desc()).offset(offset).limit(limit).all()
    return [_to_response(d, db).model_dump() for d in deployments]


@router.post("/deployments/stop-all", status_code=204)
def stop_all_deployments(
    background_tasks: BackgroundTasks,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> None:
    """Stop every running or starting deployment across all users."""
    active = db.query(Deployment).filter(
        Deployment.status.in_([DeploymentStatus.RUNNING, DeploymentStatus.STARTING])
    ).all()

    for d in active:
        d.status = DeploymentStatus.STOPPING
    db.commit()

    for d in active:
        background_tasks.add_task(lab_service.stop_lab, d.id, actor.id)

    audit_service.write_audit(
        db, action="admin.stop_all_deployments", user_id=actor.id,
        detail={"count": len(active), "triggered_by": actor.username},
        ip=ip,
    )


# "octorig-platform-api" restarts last since it's the container serving this request
_PLATFORM_CONTAINERS = [
    "octorig-platform-worker",
    "octorig-platform-beat",
    "octorig-platform-ui",
    "octorig-platform-api",
]


def _restart_platform_containers() -> None:
    for name in _PLATFORM_CONTAINERS:
        docker_service.restart_container(name)


@router.post("/platform/restart", status_code=202)
def restart_platform(
    background_tasks: BackgroundTasks,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> None:
    """Stop every active lab deployment, then restart the platform's own
    service containers (api/worker/beat/ui). The response is sent before
    any container actually restarts — including this one."""
    active = db.query(Deployment).filter(
        Deployment.status.in_([DeploymentStatus.RUNNING, DeploymentStatus.STARTING])
    ).all()

    for d in active:
        d.status = DeploymentStatus.STOPPING
    db.commit()

    for d in active:
        background_tasks.add_task(lab_service.stop_lab, d.id, actor.id)

    audit_service.write_audit(
        db, action="admin.restart_platform", user_id=actor.id,
        detail={"stopped_deployments": len(active), "triggered_by": actor.username},
        ip=ip,
    )

    background_tasks.add_task(_restart_platform_containers)


# ── Audit logs ───────────────────────────────────────────────────────────────

@router.get("/audit-logs/", response_model=list[AdminAuditLogResponse])
def list_audit_logs(
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    team_id: Optional[int] = Query(None),
    from_dt: Optional[str] = Query(None, alias="from"),
    to_dt: Optional[str] = Query(None, alias="to"),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminAuditLogResponse]:
    from datetime import datetime
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if team_id:
        q = q.filter(AuditLog.team_id == team_id)
    if from_dt:
        q = q.filter(AuditLog.created_at >= datetime.fromisoformat(from_dt))
    if to_dt:
        q = q.filter(AuditLog.created_at <= datetime.fromisoformat(to_dt))

    logs = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for log in logs:
        user = db.get(User, log.user_id) if log.user_id else None
        team = db.get(Team, log.team_id) if log.team_id else None
        result.append(
            AdminAuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                username=user.username if user else None,
                team_id=log.team_id,
                team_name=team.name if team else None,
                deployment_id=log.deployment_id,
                action=log.action,
                detail=log.detail,
                ip_address=log.ip_address,
                created_at=log.created_at,
            )
        )
    return result


# ── API Keys (all) ───────────────────────────────────────────────────────────

@router.get("/api-keys/", response_model=list[AdminApiKeyResponse])
def list_all_api_keys(
    user_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminApiKeyResponse]:
    q = db.query(ApiKey)
    if active_only:
        q = q.filter(ApiKey.is_active.is_(True))
    if user_id:
        q = q.filter(ApiKey.user_id == user_id)
    keys = q.order_by(ApiKey.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for key in keys:
        user = db.get(User, key.user_id)
        result.append(
            AdminApiKeyResponse(
                id=key.id,
                user_id=key.user_id,
                username=user.username if user else "unknown",
                name=key.name,
                key_prefix=key.key_prefix,
                expires_at=key.expires_at,
                last_used_at=key.last_used_at,
                is_active=key.is_active,
                created_at=key.created_at,
            )
        )
    return result


# ── Ranks ─────────────────────────────────────────────────────────────────────

class AdminRankResponse(BaseModel):
    id: int
    name: str
    min_points: int
    icon: Optional[str]
    color: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class AdminRankCreate(BaseModel):
    name: str
    min_points: int
    icon: Optional[str] = None
    color: Optional[str] = None


class AdminRankUpdate(BaseModel):
    name: Optional[str] = None
    min_points: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/ranks/", response_model=list[AdminRankResponse])
def list_ranks(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminRankResponse]:
    ranks = db.query(Rank).order_by(Rank.min_points.asc()).all()
    return [AdminRankResponse.model_validate(r) for r in ranks]


@router.post("/ranks/", response_model=AdminRankResponse)
def create_rank(
    body: AdminRankCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminRankResponse:
    if db.query(Rank).filter(Rank.name == body.name).first():
        raise conflict("A rank with that name already exists")
    if db.query(Rank).filter(Rank.min_points == body.min_points).first():
        raise conflict("A rank with that min_points value already exists")
    rank = Rank(
        name=body.name,
        min_points=body.min_points,
        icon=body.icon,
        color=body.color,
    )
    db.add(rank)
    db.commit()
    db.refresh(rank)
    return AdminRankResponse.model_validate(rank)


@router.patch("/ranks/{rank_id}", response_model=AdminRankResponse)
def update_rank(
    rank_id: int,
    body: AdminRankUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminRankResponse:
    rank = db.get(Rank, rank_id)
    if rank is None:
        raise not_found("Rank")
    if body.name is not None:
        existing = db.query(Rank).filter(Rank.name == body.name, Rank.id != rank_id).first()
        if existing:
            raise conflict("A rank with that name already exists")
        rank.name = body.name
    if body.min_points is not None:
        existing = db.query(Rank).filter(
            Rank.min_points == body.min_points, Rank.id != rank_id
        ).first()
        if existing:
            raise conflict("A rank with that min_points value already exists")
        rank.min_points = body.min_points
    if body.icon is not None:
        rank.icon = body.icon
    if body.color is not None:
        rank.color = body.color
    if body.is_active is not None:
        rank.is_active = body.is_active
    db.commit()
    db.refresh(rank)
    return AdminRankResponse.model_validate(rank)


@router.delete("/ranks/{rank_id}", response_model=dict)
def delete_rank(
    rank_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    rank = db.get(Rank, rank_id)
    if rank is None:
        raise not_found("Rank")
    db.delete(rank)
    db.commit()
    return {"deleted": True, "rank_id": rank_id}


# ── Site settings ─────────────────────────────────────────────────────────────

@router.get("/settings", response_model=SiteSettingsResponse)
def get_site_settings(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SiteSettingsResponse:
    return SiteSettingsResponse.model_validate(get_settings(db))


@router.patch("/settings", response_model=SiteSettingsResponse)
def update_site_settings(
    body: SiteSettingsUpdate,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> SiteSettingsResponse:
    row = get_settings(db)
    changed: dict = {}
    for field, value in body.model_dump(exclude_none=True).items():
        if getattr(row, field) != value:
            setattr(row, field, value)
            changed[field] = value
    if changed:
        db.commit()
        db.refresh(row)
        audit_service.write_audit(
            db, action="admin.settings_updated", user_id=actor.id,
            detail=changed,
            ip=ip,
        )
    return SiteSettingsResponse.model_validate(row)


# ── API Keys admin revoke ─────────────────────────────────────────────────────

@router.delete("/api-keys/{key_id}", status_code=204)
def admin_revoke_api_key(
    key_id: int,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> None:
    api_key_service.revoke_api_key(db, actor, key_id)
    audit_service.write_audit(
        db, action="admin.api_key_revoked", user_id=actor.id,
        detail={"key_id": key_id},
        ip=ip,
    )
