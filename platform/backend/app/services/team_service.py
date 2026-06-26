# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import re
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.db_types import ensure_aware
from app.core.exceptions import bad_request, conflict, not_found
from app.models.team import Team, TeamInvitation, TeamMember, TeamRole
from app.models.user import User


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")[:64]


def _unique_slug(db: Session, base: str) -> str:
    slug = base
    counter = 2
    while db.query(Team).filter(Team.slug == slug).first():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def create_team(db: Session, user: User, name: str, description: str | None = None) -> Team:
    if db.query(Team).filter(Team.name == name).first():
        raise conflict(f"A team named '{name}' already exists")

    slug = _unique_slug(db, _slugify(name))
    team = Team(
        name=name,
        slug=slug,
        description=description,
        is_personal=False,
        created_by_id=user.id,
    )
    db.add(team)
    db.flush()

    membership = TeamMember(team_id=team.id, user_id=user.id, role=TeamRole.OWNER)
    db.add(membership)
    db.commit()
    db.refresh(team)
    return team


def ensure_personal_team(db: Session, user: User) -> Team:
    """Idempotent — creates a personal team for `user` if one doesn't exist."""
    existing = (
        db.query(Team)
        .filter(
            Team.created_by_id == user.id,
            Team.is_personal.is_(True),
        )
        .first()
    )
    if existing:
        return existing

    slug = _unique_slug(db, f"personal-{_slugify(user.username)}")
    team = Team(
        name=f"{user.username}'s Personal Team",
        slug=slug,
        description=None,
        is_personal=True,
        created_by_id=user.id,
    )
    db.add(team)
    db.flush()

    membership = TeamMember(team_id=team.id, user_id=user.id, role=TeamRole.OWNER)
    db.add(membership)
    db.commit()
    db.refresh(team)
    return team


def get_user_teams(db: Session, user: User) -> list[tuple[Team, TeamMember]]:
    """Returns list of (Team, TeamMember) for all teams the user belongs to."""
    rows = (
        db.query(Team, TeamMember)
        .join(TeamMember, TeamMember.team_id == Team.id)
        .filter(TeamMember.user_id == user.id)
        .order_by(Team.is_personal.desc(), Team.name)
        .all()
    )
    return rows


def get_team_members(db: Session, team_id: int) -> list[dict]:
    rows = (
        db.query(TeamMember, User)
        .join(User, User.id == TeamMember.user_id)
        .filter(TeamMember.team_id == team_id)
        .order_by(TeamMember.joined_at)
        .all()
    )
    return [
        {
            "id": m.id,
            "team_id": m.team_id,
            "user_id": m.user_id,
            "username": u.username,
            "email": u.email,
            "role": m.role,
            "joined_at": m.joined_at,
        }
        for m, u in rows
    ]


def update_team(db: Session, team: Team, name: str | None, description: str | None) -> Team:
    if name is not None:
        if name.strip() != team.name:
            existing = db.query(Team).filter(Team.name == name.strip()).first()
            if existing and existing.id != team.id:
                raise conflict(f"A team named '{name.strip()}' already exists")
            team.name = name.strip()
    if description is not None:
        team.description = description
    db.commit()
    db.refresh(team)
    return team


def delete_team(db: Session, team: Team, db_session: Session) -> None:
    from app.models.deployment import Deployment, DeploymentStatus

    running = (
        db.query(Deployment)
        .filter(
            Deployment.team_id == team.id,
            Deployment.status.in_([DeploymentStatus.STARTING, DeploymentStatus.RUNNING]),
        )
        .count()
    )
    if running > 0:
        raise bad_request("Cannot delete team with active deployments")
    db.delete(team)
    db.commit()


def invite_member(
    db: Session, inviter: User, team: Team, username: str, role: TeamRole
) -> TeamInvitation:
    from app.services.notification_service import create_notification

    target = db.query(User).filter(User.username == username).first()
    if target is None:
        raise not_found(f"User '{username}'")

    already_member = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team.id, TeamMember.user_id == target.id)
        .first()
    )
    if already_member:
        raise conflict(f"'{username}' is already a member of this team")

    pending = (
        db.query(TeamInvitation)
        .filter(
            TeamInvitation.team_id == team.id,
            TeamInvitation.email == target.email,
            TeamInvitation.accepted_at.is_(None),
            TeamInvitation.expires_at > datetime.now(UTC),
        )
        .first()
    )
    if pending:
        raise conflict(f"An active invitation for '{username}' already exists")

    token = secrets.token_urlsafe(32)
    invitation = TeamInvitation(
        team_id=team.id,
        email=target.email,
        token=token,
        role=role,
        invited_by_id=inviter.id,
        expires_at=datetime.now(UTC) + timedelta(hours=72),
    )
    db.add(invitation)
    db.flush()

    create_notification(
        db,
        user_id=target.id,
        type="team_invite",
        title=f"You've been invited to join {team.name}",
        body=f"{inviter.username} invited you as {role.value}",
        data={
            "invitation_token": token,
            "team_id": team.id,
            "team_name": team.name,
            "inviter_username": inviter.username,
            "role": role.value,
        },
    )

    db.commit()
    db.refresh(invitation)
    return invitation


def get_invitation_by_token(db: Session, token: str) -> TeamInvitation:
    inv = db.query(TeamInvitation).filter(TeamInvitation.token == token).first()
    if inv is None:
        raise not_found("Invitation")
    if inv.accepted_at is not None:
        raise bad_request("Invitation has already been accepted")
    if ensure_aware(inv.expires_at) < datetime.now(UTC):
        raise bad_request("Invitation has expired")
    return inv


def accept_invitation(db: Session, token: str, user: User) -> TeamMember:
    inv = get_invitation_by_token(db, token)

    already = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == inv.team_id, TeamMember.user_id == user.id)
        .first()
    )
    if already:
        raise conflict("You are already a member of this team")

    membership = TeamMember(
        team_id=inv.team_id,
        user_id=user.id,
        role=inv.role,
        invited_by_id=inv.invited_by_id,
    )
    db.add(membership)

    inv.accepted_at = datetime.now(UTC)
    db.commit()
    db.refresh(membership)
    return membership


def remove_member(db: Session, team: Team, target_user_id: int) -> None:
    membership = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team.id, TeamMember.user_id == target_user_id)
        .first()
    )
    if membership is None:
        raise not_found("Team member")

    if membership.role == TeamRole.OWNER:
        owner_count = (
            db.query(TeamMember)
            .filter(TeamMember.team_id == team.id, TeamMember.role == TeamRole.OWNER)
            .count()
        )
        if owner_count <= 1:
            raise bad_request("Cannot remove the last owner of a team")

    db.delete(membership)
    db.commit()


def change_member_role(
    db: Session, team: Team, target_user_id: int, new_role: TeamRole
) -> TeamMember:
    membership = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team.id, TeamMember.user_id == target_user_id)
        .first()
    )
    if membership is None:
        raise not_found("Team member")

    if membership.role == TeamRole.OWNER and new_role != TeamRole.OWNER:
        owner_count = (
            db.query(TeamMember)
            .filter(TeamMember.team_id == team.id, TeamMember.role == TeamRole.OWNER)
            .count()
        )
        if owner_count <= 1:
            raise bad_request("Cannot demote the last owner of a team")

    membership.role = new_role
    db.commit()
    db.refresh(membership)
    return membership


def transfer_ownership(db: Session, team: Team, actor: User, new_owner_id: int) -> None:
    new_owner_membership = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team.id, TeamMember.user_id == new_owner_id)
        .first()
    )
    if new_owner_membership is None:
        raise bad_request("Target user is not a member of this team")

    actor_membership = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team.id, TeamMember.user_id == actor.id)
        .first()
    )
    if actor_membership and actor_membership.role == TeamRole.OWNER:
        actor_membership.role = TeamRole.MANAGER

    new_owner_membership.role = TeamRole.OWNER
    db.commit()
