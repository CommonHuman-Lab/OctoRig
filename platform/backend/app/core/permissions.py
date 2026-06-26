# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
RBAC permission constants and checking functions.

All access is driven by PlatformRole assignments on User.platform_roles —
there are no standalone admin/superuser flags. The "admin" system role
(seeded with every permission) is what makes a user platform-wide privileged.
"""

from sqlalchemy.orm import Session

from app.models.deployment import Deployment
from app.models.team import TeamMember, TeamRole
from app.models.user import User

# ── Role ordering for comparisons ───────────────────────────────────────────

_ROLE_RANK: dict[TeamRole, int] = {
    TeamRole.VIEWER: 0,
    TeamRole.MEMBER: 1,
    TeamRole.MANAGER: 2,
    TeamRole.OWNER: 3,
}


def role_gte(membership: TeamMember | None, minimum: TeamRole) -> bool:
    """True if the membership role is >= the minimum required role."""
    if membership is None:
        return False
    return _ROLE_RANK[membership.role] >= _ROLE_RANK[minimum]


# ── Platform permission keys ────────────────────────────────────────────────

PERM_PLATFORM_DASHBOARD = "platform.dashboard"
PERM_PLATFORM_CHALLENGES = "platform.challenges"
PERM_PLATFORM_EVENTS = "platform.events"
PERM_PLATFORM_SCOREBOARD = "platform.scoreboard"
PERM_PLATFORM_BADGES = "platform.badges"
PERM_PLATFORM_LABS = "platform.labs"
PERM_PLATFORM_DEPLOYMENTS = "platform.deployments"
PERM_PLATFORM_TEAMS = "platform.teams"

ALL_PLATFORM_PERMS = [
    PERM_PLATFORM_DASHBOARD, PERM_PLATFORM_CHALLENGES, PERM_PLATFORM_EVENTS,
    PERM_PLATFORM_SCOREBOARD, PERM_PLATFORM_BADGES, PERM_PLATFORM_LABS,
    PERM_PLATFORM_DEPLOYMENTS, PERM_PLATFORM_TEAMS,
]

PERM_ADMIN_PANEL = "admin.panel"
PERM_ADMIN_USERS_VIEW = "admin.users.view"
PERM_ADMIN_USERS_MANAGE = "admin.users.manage"
PERM_ADMIN_TEAMS_VIEW = "admin.teams.view"
PERM_ADMIN_DEPLOYMENTS_VIEW = "admin.deployments.view"
PERM_ADMIN_DEPLOYMENTS_MANAGE = "admin.deployments.manage"
PERM_ADMIN_AUDIT_VIEW = "admin.audit.view"
PERM_ADMIN_CHALLENGES_MANAGE = "admin.challenges.manage"
PERM_ADMIN_EVENTS_MANAGE = "admin.events.manage"
PERM_ADMIN_API_KEYS_VIEW = "admin.api_keys.view"
PERM_ADMIN_RANKS_MANAGE = "admin.ranks.manage"
PERM_ADMIN_ASSESSMENTS_MANAGE = "admin.assessments.manage"
PERM_ADMIN_CONTENT_MANAGE = "admin.content.manage"
PERM_ADMIN_SETTINGS_MANAGE = "admin.settings.manage"

ALL_ADMIN_PERMS = [
    PERM_ADMIN_PANEL, PERM_ADMIN_USERS_VIEW, PERM_ADMIN_USERS_MANAGE,
    PERM_ADMIN_TEAMS_VIEW, PERM_ADMIN_DEPLOYMENTS_VIEW, PERM_ADMIN_DEPLOYMENTS_MANAGE,
    PERM_ADMIN_AUDIT_VIEW, PERM_ADMIN_CHALLENGES_MANAGE, PERM_ADMIN_EVENTS_MANAGE,
    PERM_ADMIN_API_KEYS_VIEW, PERM_ADMIN_RANKS_MANAGE, PERM_ADMIN_ASSESSMENTS_MANAGE,
    PERM_ADMIN_CONTENT_MANAGE, PERM_ADMIN_SETTINGS_MANAGE,
]

PERM_CREATOR_ACCESS = "creator.access"

ALL_PERMS = ALL_PLATFORM_PERMS + ALL_ADMIN_PERMS + [PERM_CREATOR_ACCESS]


def resolve_permissions(user: User, db: Session) -> list[str]:
    """Resolve the full permission set granted to a user from their assigned roles."""
    if not user.platform_roles:
        return []

    from app.models.role import PlatformRole

    roles = db.query(PlatformRole).filter(PlatformRole.slug.in_(user.platform_roles)).all()
    perms: set[str] = set()
    for role in roles:
        perms.update(role.permissions or [])
    return sorted(perms)


def is_privileged(user: User, db: Session) -> bool:
    """True if the user holds platform-wide admin access (the admin.panel permission)."""
    return PERM_ADMIN_PANEL in resolve_permissions(user, db)


# ── Deployment checks ────────────────────────────────────────────────────────

def can_deploy(user: User, db: Session, membership: TeamMember | None = None) -> bool:
    if is_privileged(user, db):
        return True
    if membership is None:
        return True  # personal deployment
    return role_gte(membership, TeamRole.MEMBER)


def can_destroy_deployment(
    user: User,
    db: Session,
    deployment: Deployment,
    membership: TeamMember | None = None,
) -> bool:
    if is_privileged(user, db):
        return True
    if deployment.started_by_id == user.id:
        return True
    if deployment.team_id is not None and membership is not None:
        return role_gte(membership, TeamRole.MANAGER)
    return False


def can_view_logs(
    user: User, db: Session, deployment: Deployment, membership: TeamMember | None = None
) -> bool:
    if is_privileged(user, db):
        return True
    if deployment.started_by_id == user.id:
        return True
    if deployment.team_id is not None and membership is not None:
        return role_gte(membership, TeamRole.VIEWER)
    if deployment.visibility == "public":
        return True
    return False


# ── Team checks ──────────────────────────────────────────────────────────────

def can_manage_team(user: User, db: Session, membership: TeamMember | None = None) -> bool:
    """Update name/description, manage settings."""
    if is_privileged(user, db):
        return True
    return role_gte(membership, TeamRole.MANAGER)


def can_delete_team(user: User, db: Session, membership: TeamMember | None = None) -> bool:
    if is_privileged(user, db):
        return True
    return role_gte(membership, TeamRole.OWNER)


def can_invite_members(user: User, db: Session, membership: TeamMember | None = None) -> bool:
    if is_privileged(user, db):
        return True
    return role_gte(membership, TeamRole.MANAGER)


def can_remove_member(user: User, db: Session, membership: TeamMember | None = None) -> bool:
    if is_privileged(user, db):
        return True
    return role_gte(membership, TeamRole.MANAGER)


def can_change_member_role(user: User, db: Session, membership: TeamMember | None = None) -> bool:
    if is_privileged(user, db):
        return True
    return role_gte(membership, TeamRole.MANAGER)


def can_transfer_ownership(user: User, db: Session, membership: TeamMember | None = None) -> bool:
    if is_privileged(user, db):
        return True
    return role_gte(membership, TeamRole.OWNER)


def can_view_team_audit(user: User, db: Session, membership: TeamMember | None = None) -> bool:
    if is_privileged(user, db):
        return True
    return role_gte(membership, TeamRole.MANAGER)


# ── Admin checks ─────────────────────────────────────────────────────────────

def can_manage_templates(user: User, db: Session) -> bool:
    return is_privileged(user, db)


def can_manage_users(user: User, db: Session) -> bool:
    return is_privileged(user, db)


def can_view_all_audit_logs(user: User, db: Session) -> bool:
    return is_privileged(user, db)


def can_schedule(user: User, db: Session, membership: TeamMember | None = None) -> bool:
    if is_privileged(user, db):
        return True
    if membership is None:
        return True  # personal schedule
    return role_gte(membership, TeamRole.MEMBER)
