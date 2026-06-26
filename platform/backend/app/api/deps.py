# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import UTC

from fastapi import Depends, Query, Request, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import credentials_exception, forbidden_exception, not_found
from app.core.security import decode_access_token
from app.database import get_db
from app.models.deployment import Deployment
from app.models.role import PlatformRole
from app.models.team import Team, TeamMember, TeamRole
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_ROLE_RANK: dict[TeamRole, int] = {
    TeamRole.VIEWER: 0,
    TeamRole.MEMBER: 1,
    TeamRole.MANAGER: 2,
    TeamRole.OWNER: 3,
}


def _get_user_from_token(token: str, db: Session) -> User:
    try:
        user_id = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def _get_user_from_api_key(raw_key: str, db: Session) -> User | None:
    from datetime import datetime

    from app.core.security import verify_password
    from app.models.api_key import ApiKey

    if not raw_key.startswith("oktor_"):
        return None
    prefix = raw_key[6:14]  # 8 chars after "oktor_"
    keys = (
        db.query(ApiKey)
        .filter(
            ApiKey.key_prefix == prefix,
            ApiKey.is_active.is_(True),
        )
        .all()
    )

    now = datetime.now(UTC)
    for key in keys:
        if key.expires_at and key.expires_at < now:
            continue
        if verify_password(raw_key, key.hashed_key):
            key.last_used_at = now
            db.commit()
            user = db.get(User, key.user_id)
            if user and user.is_active:
                return user
    return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise credentials_exception
    return _get_user_from_token(credentials.credentials, db)


def get_current_user_from_query(
    token: str = Query(...),
    db: Session = Depends(get_db),
) -> User:
    """For WebSocket endpoints where headers can't carry the token."""
    return _get_user_from_token(token, db)


def get_current_user_or_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    api_key: str | None = Security(api_key_header),
    db: Session = Depends(get_db),
) -> User:
    """Accepts either a JWT Bearer token or an X-API-Key header."""
    if credentials is not None:
        return _get_user_from_token(credentials.credentials, db)
    if api_key is not None:
        user = _get_user_from_api_key(api_key, db)
        if user is not None:
            return user
    raise credentials_exception


def require_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    from app.core.permissions import is_privileged

    if not is_privileged(current_user, db):
        raise forbidden_exception
    return current_user


def get_team_or_404(team_id: int, db: Session = Depends(get_db)) -> Team:
    team = db.get(Team, team_id)
    if team is None:
        raise not_found("Team")
    return team


def get_user_or_404(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise not_found("User")
    return user


def get_deployment_or_404(deployment_id: int, db: Session = Depends(get_db)) -> Deployment:
    deployment = db.get(Deployment, deployment_id)
    if deployment is None:
        raise not_found("Deployment")
    return deployment


def get_role_or_404(slug: str, db: Session = Depends(get_db)) -> PlatformRole:
    role = db.query(PlatformRole).filter(PlatformRole.slug == slug).first()
    if role is None:
        raise not_found("Role")
    return role


def get_client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def get_team_membership(
    team_id: int,
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
) -> TeamMember | None:
    """Returns the current user's TeamMember row for the given team, or None."""
    return (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id)
        .first()
    )


def require_team_role(minimum: TeamRole):
    """Dependency factory — requires the caller to have at least `minimum` role."""

    def _check(
        membership: TeamMember | None = Depends(get_team_membership),
        current_user: User = Depends(get_current_user_or_api_key),
        db: Session = Depends(get_db),
    ) -> TeamMember:
        from app.core.permissions import is_privileged

        if is_privileged(current_user, db):
            return membership  # type: ignore[return-value]
        if membership is None or _ROLE_RANK[membership.role] < _ROLE_RANK[minimum]:
            raise forbidden_exception
        return membership

    return _check
