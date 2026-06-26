# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import secrets
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import not_found
from app.core.security import hash_password, verify_password
from app.models.api_key import ApiKey
from app.models.user import User

_PREFIX = "oktor_"
_KEY_BYTES = 32  # generates ~43-char base64url string


def create_api_key(
    db: Session,
    user: User,
    name: str,
    expires_at: datetime | None = None,
) -> tuple[ApiKey, str]:
    """
    Returns (ApiKey, raw_key). The raw_key is shown ONCE to the caller.
    Only the bcrypt hash is persisted.
    """
    random_part = secrets.token_urlsafe(_KEY_BYTES)
    raw_key = f"{_PREFIX}{random_part}"
    prefix = random_part[:8]

    key = ApiKey(
        user_id=user.id,
        name=name,
        key_prefix=prefix,
        hashed_key=hash_password(raw_key),
        expires_at=expires_at,
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return key, raw_key


def revoke_api_key(db: Session, user: User, key_id: int) -> None:
    key = db.get(ApiKey, key_id)
    if key is None:
        raise not_found("API key")
    from app.core.permissions import is_privileged

    if key.user_id != user.id and not is_privileged(user, db):
        raise not_found("API key")
    key.is_active = False
    db.commit()


def list_api_keys(db: Session, user: User) -> list[ApiKey]:
    return (
        db.query(ApiKey).filter(ApiKey.user_id == user.id).order_by(ApiKey.created_at.desc()).all()
    )


def verify_api_key(db: Session, raw_key: str) -> User | None:
    """Verify a raw key against stored hashes. Returns the owning User or None."""
    if not raw_key.startswith(_PREFIX):
        return None
    prefix = raw_key[len(_PREFIX) : len(_PREFIX) + 8]

    candidates = (
        db.query(ApiKey)
        .filter(
            ApiKey.key_prefix == prefix,
            ApiKey.is_active.is_(True),
        )
        .all()
    )

    now = datetime.now(UTC)
    for key in candidates:
        if key.expires_at and key.expires_at.replace(tzinfo=UTC) < now:
            continue
        if verify_password(raw_key, key.hashed_key):
            key.last_used_at = now
            db.commit()
            user = db.get(User, key.user_id)
            if user and user.is_active:
                return user
    return None
