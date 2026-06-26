# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

# ── Action constants ─────────────────────────────────────────────────────────

AUTH_LOGIN = "auth.login"
AUTH_LOGOUT = "auth.logout"
AUTH_LOGIN_FAILED = "auth.login_failed"
AUTH_API_KEY_USED = "auth.api_key_used"

TEAM_CREATED = "team.created"
TEAM_UPDATED = "team.updated"
TEAM_DELETED = "team.deleted"
TEAM_MEMBER_INVITED = "team.member_invited"
TEAM_MEMBER_JOINED = "team.member_joined"
TEAM_MEMBER_REMOVED = "team.member_removed"
TEAM_MEMBER_ROLE_CHANGED = "team.member_role_changed"
TEAM_OWNERSHIP_TRANSFERRED = "team.ownership_transferred"

LAB_DEPLOYED = "lab.deployed"
LAB_DEPLOY_FAILED = "lab.deploy_failed"
LAB_DESTROYED = "lab.destroyed"
LAB_RESET = "lab.reset"

API_KEY_CREATED = "api_key.created"
API_KEY_REVOKED = "api_key.revoked"

ADMIN_USER_CREATED = "admin.user_created"
ADMIN_USER_DEACTIVATED = "admin.user_deactivated"
ADMIN_ROLE_CHANGED = "admin.role_changed"
ADMIN_LAB_TOGGLED = "admin.lab_toggled"

SCHEDULE_CREATED = "schedule.created"
SCHEDULE_CANCELLED = "schedule.cancelled"
SCHEDULE_EXECUTED = "schedule.executed"

CHALLENGE_SUBMITTED = "challenge.submitted"
CHALLENGE_SOLVED = "challenge.solved"
CHALLENGE_CREATED = "challenge.created"
CHALLENGE_UPDATED = "challenge.updated"
CHALLENGE_ARCHIVED = "challenge.archived"

BADGE_AWARDED = "badge.awarded"

CONTENT_SUBMITTED = "content.submitted"
CONTENT_PUBLISHED = "content.published"
CONTENT_REJECTED = "content.rejected"

MARKETPLACE_INSTALLED = "marketplace.installed"
MARKETPLACE_UNINSTALLED = "marketplace.uninstalled"


def write_audit(
    db: Session,
    action: str,
    user_id: int | None = None,
    team_id: int | None = None,
    deployment_id: int | None = None,
    detail: dict[str, Any] | None = None,
    ip: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        action=action,
        user_id=user_id,
        team_id=team_id,
        deployment_id=deployment_id,
        detail=detail or {},
        ip_address=ip,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
