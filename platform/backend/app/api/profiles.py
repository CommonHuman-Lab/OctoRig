# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.pagination import NarrowLimit
from app.models.user import User
from app.services.profile_service import get_profile, update_profile

router = APIRouter(prefix="/profiles", tags=["profiles"])


class ProfileUpdateRequest(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    website_url: Optional[str] = None
    location: Optional[str] = None
    github_handle: Optional[str] = None
    privacy_level: Optional[str] = None
    show_activity: Optional[bool] = None
    theme: Optional[str] = None
    locale: Optional[str] = None


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
