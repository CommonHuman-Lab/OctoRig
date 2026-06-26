# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.pagination import NarrowLimit
from app.models.user import User
from app.services.profile_service import get_profile, update_profile

router = APIRouter(prefix="/profiles", tags=["profiles"])


class ProfileUpdateRequest(BaseModel):
    bio: str | None = None
    avatar_url: str | None = None
    website_url: str | None = None
    location: str | None = None
    github_handle: str | None = None
    privacy_level: str | None = None
    show_activity: bool | None = None
    theme: str | None = None
    locale: str | None = None


@router.get("/me", response_model=dict[str, Any])
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    return get_profile(db, current_user.username, viewer_id=current_user.id)


@router.patch("/me", response_model=dict[str, Any])
def update_my_profile(
    body: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    update_profile(
        db,
        user_id=current_user.id,
        bio=body.bio,
        avatar_url=body.avatar_url,
        website_url=body.website_url,
        location=body.location,
        github_handle=body.github_handle,
        privacy_level=body.privacy_level,
        show_activity=body.show_activity,
        theme=body.theme,
        locale=body.locale,
    )
    return get_profile(db, current_user.username, viewer_id=current_user.id)


class UserSearchResult(BaseModel):
    id: int
    username: str


@router.get("/search", response_model=list[UserSearchResult])
def search_users(
    q: str = Query("", min_length=1),
    limit: NarrowLimit = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserSearchResult]:
    results = (
        db.query(User)
        .filter(
            User.username.ilike(f"%{q}%"),
            User.is_active.is_(True),
            User.id != current_user.id,
        )
        .order_by(User.username)
        .limit(limit)
        .all()
    )
    return [UserSearchResult(id=u.id, username=u.username) for u in results]


@router.get("/{username}", response_model=dict[str, Any])
def get_user_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    return get_profile(db, username, viewer_id=current_user.id)
