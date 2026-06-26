# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.models.badge import BadgeDefinition, UserBadge
from app.models.user import User
from app.services.achievement_service import award_badge, evaluate_achievements
from app.services.profile_service import ensure_profile_visible

router = APIRouter(prefix="/badges", tags=["badges"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class BadgeSummary(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    icon: str
    category: Optional[str]
    points_value: int
    earned: bool = False
    earned_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ManualAwardRequest(BaseModel):
    user_id: int
    note: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _from_user_badge(ub: UserBadge) -> BadgeSummary:
    return BadgeSummary(
        id=ub.badge.id,
        slug=ub.badge.slug,
        name=ub.badge.name,
        description=ub.badge.description,
        icon=ub.badge.icon,
        category=ub.badge.category,
        points_value=ub.badge.points_value,
        earned=True,
        earned_at=ub.awarded_at,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[BadgeSummary])
def list_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BadgeSummary]:
    badges = (
        db.query(BadgeDefinition)
        .filter(BadgeDefinition.is_active.is_(True))
        .order_by(BadgeDefinition.category, BadgeDefinition.name)
        .all()
    )
    earned_map: dict[int, datetime] = {
        ub.badge_id: ub.awarded_at
        for ub in db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()
    }
    return [
        BadgeSummary(
            id=b.id,
            slug=b.slug,
            name=b.name,
            description=b.description,
            icon=b.icon,
            category=b.category,
            points_value=b.points_value,
            earned=b.id in earned_map,
            earned_at=earned_map.get(b.id),
        )
        for b in badges
    ]


@router.get("/me", response_model=list[BadgeSummary])
def my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BadgeSummary]:
    user_badges = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == current_user.id)
        .order_by(UserBadge.awarded_at.desc())
        .all()
    )
    return [_from_user_badge(ub) for ub in user_badges]


@router.get("/users/{user_id}", response_model=list[BadgeSummary])
def user_badges_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BadgeSummary]:
    ensure_profile_visible(db, current_user.id, user_id)
    user_badges = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user_id)
        .order_by(UserBadge.awarded_at.desc())
        .all()
    )
    return [_from_user_badge(ub) for ub in user_badges]


@router.post("/evaluate", response_model=list[str])
def evaluate_my_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[str]:
    return evaluate_achievements(db, current_user.id)


@router.post("/{badge_slug}/award", response_model=dict, dependencies=[Depends(require_admin)])
def manual_award(
    badge_slug: str = Path(...),
    body: ManualAwardRequest = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    badge = db.query(BadgeDefinition).filter(BadgeDefinition.slug == badge_slug).first()
    if badge is None:
        from app.core.exceptions import not_found
        raise not_found("Badge")
    ub = award_badge(db, body.user_id, badge, awarded_by_id=current_user.id, note=body.note)
    if ub is None:
        return {"awarded": False, "message": "User already has this badge"}
    return {"awarded": True, "badge_slug": badge.slug, "user_id": body.user_id}
