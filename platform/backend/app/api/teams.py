# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import (
    get_client_ip,
    get_current_user,
    get_current_user_or_api_key,
    get_team_membership,
    get_team_or_404,
)
from app.core.exceptions import forbidden_exception, not_found
from app.core.permissions import (
    can_change_member_role,
    can_delete_team,
    can_invite_members,
    can_manage_team,
    can_remove_member,
    can_transfer_ownership,
    is_privileged,
)
from app.database import get_db
from app.models.team import Team, TeamInvitation, TeamMember, TeamRole
from app.models.user import User
from app.schemas.team import (
    ChangeMemberRoleRequest,
    InvitationDetail,
    InvitationResponse,
    InviteRequest,
    MemberResponse,
    TeamCreate,
    TeamResponse,
    TeamUpdate,
    TeamWithRole,
    TransferOwnershipRequest,
)
from app.services import audit_service, team_service

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/", response_model=list[TeamWithRole])
def list_teams(
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
) -> list[TeamWithRole]:
    rows = team_service.get_user_teams(db, current_user)
    result = []
    for team, membership in rows:
        member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
        result.append(
            TeamWithRole(
                **TeamResponse.model_validate(team).model_dump(),
                my_role=membership.role,
                member_count=member_count,
            )
        )
    return result


@router.post("/", response_model=TeamWithRole, status_code=201)
def create_team(
    payload: TeamCreate,
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    ip: str | None = Depends(get_client_ip),
) -> TeamWithRole:
    team = team_service.create_team(db, current_user, payload.name, payload.description)
    audit_service.write_audit(
        db,
        action="team.created",
        user_id=current_user.id,
        team_id=team.id,
        detail={"name": team.name},
        ip=ip,
    )
    membership = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id)
        .first()
    )
    return TeamWithRole(
        **TeamResponse.model_validate(team).model_dump(),
        my_role=membership.role,
        member_count=1,
    )


@router.get("/{team_id}", response_model=TeamWithRole)
def get_team(
    team: Team = Depends(get_team_or_404),
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    membership: TeamMember | None = Depends(get_team_membership),
) -> TeamWithRole:
    if membership is None and not is_privileged(current_user, db):
        raise not_found("Team")
    member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
    role = membership.role if membership else TeamRole.VIEWER
    return TeamWithRole(
        **TeamResponse.model_validate(team).model_dump(),
        my_role=role,
        member_count=member_count,
    )


@router.patch("/{team_id}", response_model=TeamResponse)
def update_team(
    payload: TeamUpdate,
    team: Team = Depends(get_team_or_404),
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    membership: TeamMember | None = Depends(get_team_membership),
    ip: str | None = Depends(get_client_ip),
) -> TeamResponse:
    if membership is None and not is_privileged(current_user, db):
        raise not_found("Team")
    if not can_manage_team(current_user, db, membership):
        raise forbidden_exception
    team = team_service.update_team(db, team, payload.name, payload.description)
    audit_service.write_audit(
        db,
        action="team.updated",
        user_id=current_user.id,
        team_id=team.id,
        ip=ip,
    )
    return TeamResponse.model_validate(team)


@router.delete("/{team_id}", status_code=204)
def delete_team(
    team: Team = Depends(get_team_or_404),
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    membership: TeamMember | None = Depends(get_team_membership),
    ip: str | None = Depends(get_client_ip),
) -> None:
    if membership is None and not is_privileged(current_user, db):
        raise not_found("Team")
    if not can_delete_team(current_user, db, membership):
        raise forbidden_exception
    if team.is_personal:
        from app.core.exceptions import bad_request

        raise bad_request("Personal teams cannot be deleted")
    audit_service.write_audit(
        db,
        action="team.deleted",
        user_id=current_user.id,
        team_id=team.id,
        detail={"name": team.name},
        ip=ip,
    )
    team_service.delete_team(db, team, db)


@router.get("/{team_id}/members", response_model=list[MemberResponse])
def list_members(
    team: Team = Depends(get_team_or_404),
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    membership: TeamMember | None = Depends(get_team_membership),
) -> list[MemberResponse]:
    if membership is None and not is_privileged(current_user, db):
        raise not_found("Team")
    rows = team_service.get_team_members(db, team.id)
    return [MemberResponse(**r) for r in rows]


@router.post("/{team_id}/invite", response_model=InvitationResponse, status_code=201)
def invite_member(
    payload: InviteRequest,
    team: Team = Depends(get_team_or_404),
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    membership: TeamMember | None = Depends(get_team_membership),
    ip: str | None = Depends(get_client_ip),
) -> InvitationResponse:
    if membership is None and not is_privileged(current_user, db):
        raise not_found("Team")
    if not can_invite_members(current_user, db, membership):
        raise forbidden_exception
    inv = team_service.invite_member(db, current_user, team, payload.username, payload.role)
    audit_service.write_audit(
        db,
        action="team.member_invited",
        user_id=current_user.id,
        team_id=team.id,
        detail={"username": payload.username, "role": payload.role.value},
        ip=ip,
    )
    return InvitationResponse.model_validate(inv)


@router.delete("/{team_id}/members/{user_id}", status_code=204)
def remove_member(
    user_id: int,
    team: Team = Depends(get_team_or_404),
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    membership: TeamMember | None = Depends(get_team_membership),
    ip: str | None = Depends(get_client_ip),
) -> None:
    # A user can remove themselves regardless of role
    if user_id != current_user.id:
        if membership is None and not is_privileged(current_user, db):
            raise not_found("Team")
        if not can_remove_member(current_user, db, membership):
            raise forbidden_exception
    team_service.remove_member(db, team, user_id)
    audit_service.write_audit(
        db,
        action="team.member_removed",
        user_id=current_user.id,
        team_id=team.id,
        detail={"removed_user_id": user_id},
        ip=ip,
    )


@router.patch("/{team_id}/members/{user_id}", response_model=MemberResponse)
def change_member_role(
    user_id: int,
    payload: ChangeMemberRoleRequest,
    team: Team = Depends(get_team_or_404),
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    membership: TeamMember | None = Depends(get_team_membership),
    ip: str | None = Depends(get_client_ip),
) -> MemberResponse:
    if membership is None and not is_privileged(current_user, db):
        raise not_found("Team")
    if not can_change_member_role(current_user, db, membership):
        raise forbidden_exception
    updated = team_service.change_member_role(db, team, user_id, payload.role)
    audit_service.write_audit(
        db,
        action="team.member_role_changed",
        user_id=current_user.id,
        team_id=team.id,
        detail={"target_user_id": user_id, "new_role": payload.role.value},
        ip=ip,
    )
    target_user = db.get(User, user_id)
    return MemberResponse(
        id=updated.id,
        team_id=updated.team_id,
        user_id=updated.user_id,
        username=target_user.username if target_user else "",
        email=target_user.email if target_user else "",
        role=updated.role,
        joined_at=updated.joined_at,
    )


@router.post("/{team_id}/transfer", status_code=204)
def transfer_ownership(
    payload: TransferOwnershipRequest,
    team: Team = Depends(get_team_or_404),
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    membership: TeamMember | None = Depends(get_team_membership),
    ip: str | None = Depends(get_client_ip),
) -> None:
    if membership is None and not is_privileged(current_user, db):
        raise not_found("Team")
    if not can_transfer_ownership(current_user, db, membership):
        raise forbidden_exception
    team_service.transfer_ownership(db, team, current_user, payload.new_owner_id)
    audit_service.write_audit(
        db,
        action="team.ownership_transferred",
        user_id=current_user.id,
        team_id=team.id,
        detail={"new_owner_id": payload.new_owner_id},
        ip=ip,
    )


# ── Invitation endpoints (no team_id prefix) ────────────────────────────────

invitations_router = APIRouter(prefix="/invitations", tags=["invitations"])


@invitations_router.get("/{token}", response_model=InvitationDetail)
def get_invitation(token: str, db: Session = Depends(get_db)) -> InvitationDetail:
    inv = team_service.get_invitation_by_token(db, token)
    team = db.get(Team, inv.team_id)
    inviter = db.get(User, inv.invited_by_id)
    return InvitationDetail(
        team_name=team.name if team else "",
        team_slug=team.slug if team else "",
        role=inv.role,
        invited_by_username=inviter.username if inviter else "",
        expires_at=inv.expires_at,
    )


@invitations_router.post("/{token}/decline", status_code=204)
def decline_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    inv = db.query(TeamInvitation).filter(TeamInvitation.token == token).first()
    if inv is None or inv.accepted_at is not None:
        return
    db.delete(inv)
    db.commit()


@invitations_router.post("/{token}/accept", response_model=MemberResponse, status_code=201)
def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ip: str | None = Depends(get_client_ip),
) -> MemberResponse:
    membership = team_service.accept_invitation(db, token, current_user)
    audit_service.write_audit(
        db,
        action="team.member_joined",
        user_id=current_user.id,
        team_id=membership.team_id,
        detail={"role": membership.role.value},
        ip=ip,
    )
    return MemberResponse(
        id=membership.id,
        team_id=membership.team_id,
        user_id=membership.user_id,
        username=current_user.username,
        email=current_user.email,
        role=membership.role,
        joined_at=membership.joined_at,
    )
