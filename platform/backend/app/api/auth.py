# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.api.deps import get_client_ip, get_current_user, get_current_user_or_api_key
from app.core.db_helpers import raise_if_exists
from app.config import settings
from app.core.exceptions import bad_request, credentials_exception, forbidden_exception, too_many_requests
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    generate_opaque_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.database import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.admin import PublicSettingsResponse
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services import audit_service, login_lockout_service
from app.services.audit_service import write_audit
from app.services.settings_service import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_NAME = "octorig_refresh_token"
_COOKIE_PATH = "/api/v1/auth"


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=not settings.debug,
        path=_COOKIE_PATH,
        max_age=settings.refresh_token_expire_days * 86_400,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=_COOKIE_NAME, path=_COOKIE_PATH)


def _issue_refresh_token(db: Session, user_id: int) -> str:
    """Generate, store (hashed), and return a plain refresh token."""
    raw = generate_opaque_token()
    expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    db.add(RefreshToken(user_id=user_id, token_hash=hash_token(raw), expires_at=expires))
    db.commit()
    return raw


def _purge_expired(db: Session, user_id: int) -> None:
    """Delete expired (not just revoked) tokens for this user to keep the table lean."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.expires_at < datetime.now(timezone.utc),
    ).delete(synchronize_session=False)
    db.commit()


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    ip = get_client_ip(request)

    if user is not None and login_lockout_service.is_locked(user):
        write_audit(db, action=audit_service.AUTH_LOGIN_FAILED,
                    detail={"username": payload.username, "reason": "locked"}, ip=ip)
        raise too_many_requests("Account temporarily locked due to repeated failed login attempts")

    if user is None or not verify_password(payload.password, user.hashed_password):
        if user is not None:
            login_lockout_service.record_failed_attempt(user)
            db.commit()
        write_audit(db, action=audit_service.AUTH_LOGIN_FAILED,
                    detail={"username": payload.username}, ip=ip)
        raise credentials_exception

    if not user.is_active:
        write_audit(db, action=audit_service.AUTH_LOGIN_FAILED,
                    detail={"username": payload.username, "reason": "inactive"}, ip=ip)
        raise credentials_exception

    login_lockout_service.reset(user)
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    write_audit(db, action=audit_service.AUTH_LOGIN, user_id=user.id, ip=ip)

    from app.services.team_service import ensure_personal_team
    ensure_personal_team(db, user)

    _purge_expired(db, user.id)
    raw_refresh = _issue_refresh_token(db, user.id)
    _set_refresh_cookie(response, raw_refresh)

    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Exchange a valid refresh token cookie for a new access token.
    The old refresh token is revoked and a new one is issued (rotation).
    """
    raw = request.cookies.get(_COOKIE_NAME)
    if not raw:
        raise credentials_exception

    token_hash = hash_token(raw)
    rt = db.query(RefreshToken).filter_by(token_hash=token_hash).first()

    now = datetime.now(timezone.utc)
    if rt is None or rt.revoked or rt.expires_at.replace(tzinfo=timezone.utc) < now:
        _clear_refresh_cookie(response)
        raise credentials_exception

    user = db.get(User, rt.user_id)
    if user is None or not user.is_active:
        _clear_refresh_cookie(response)
        raise credentials_exception

    # Rotate: revoke the old token, issue a new one
    rt.revoked = True
    db.commit()

    raw_new = _issue_refresh_token(db, user.id)
    _set_refresh_cookie(response, raw_new)

    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    raw = request.cookies.get(_COOKIE_NAME)
    if raw:
        rt = db.query(RefreshToken).filter_by(
            token_hash=hash_token(raw), user_id=current_user.id
        ).first()
        if rt:
            rt.revoked = True
            db.commit()
    _clear_refresh_cookie(response)
    write_audit(db, action=audit_service.AUTH_LOGOUT, user_id=current_user.id)
    return {"message": "logged out"}


@router.get("/me", response_model=UserResponse)
def me(
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
) -> UserResponse:
    from app.core.permissions import resolve_permissions

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_candidate=current_user.is_candidate,
        platform_roles=current_user.platform_roles or [],
        permissions=resolve_permissions(current_user, db),
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
    )


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password", status_code=204)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise bad_request("Current password is incorrect")
    if len(payload.new_password) < 8:
        raise bad_request("New password must be at least 8 characters")
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    write_audit(db, action="auth.password_changed", user_id=current_user.id)


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("10/minute")
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    ip = get_client_ip(request)
    site = get_settings(db)
    if not site.registration_open:
        raise forbidden_exception

    if len(payload.password) < 8:
        raise bad_request("Password must be at least 8 characters")
    raise_if_exists(db, User, f"Username '{payload.username}' is already taken", username=payload.username)
    raise_if_exists(db, User, f"Email '{payload.email}' is already registered", email=payload.email)

    from app.models.role import PlatformRole

    default_slugs = [r.slug for r in db.query(PlatformRole.slug).filter(PlatformRole.is_default.is_(True)).all()]

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_active=True,
        platform_roles=default_slugs,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    from app.services.team_service import ensure_personal_team
    ensure_personal_team(db, user)

    write_audit(db, action="auth.registered", user_id=user.id, ip=ip)

    _purge_expired(db, user.id)
    raw_refresh = _issue_refresh_token(db, user.id)
    _set_refresh_cookie(response, raw_refresh)

    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/settings/public", response_model=PublicSettingsResponse)
def public_settings(db: Session = Depends(get_db)) -> PublicSettingsResponse:
    row = get_settings(db)
    return PublicSettingsResponse(
        registration_open=row.registration_open,
        maintenance_mode=row.maintenance_mode,
        maintenance_message=row.maintenance_message,
        first_blood_enabled=row.first_blood_enabled,
        python_editor_enabled=row.python_editor_enabled,
        company_name=row.company_name,
        company_logo_url=row.company_logo_url,
        default_theme=row.default_theme,
    )
