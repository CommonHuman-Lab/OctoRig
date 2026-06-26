# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.rank import Rank
from app.models.user import User
from app.services.profile_service import ensure_profile_visible
from app.services.rank_service import get_next_rank, get_rank_for_points
from app.services.scoring_service import get_user_score

router = APIRouter(prefix="/ranks", tags=["ranks"])


class RankResponse(BaseModel):
    id: int
    name: str
    min_points: int
    icon: str | None
    color: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class UserRankResponse(BaseModel):
    points: int
    rank: RankResponse | None
    next_rank: RankResponse | None
    progress_pct: float


def _build_user_rank(db: Session, user_id: int) -> UserRankResponse:
    points = get_user_score(db, user_id)
    rank = get_rank_for_points(db, points)
    next_rank = get_next_rank(db, points)

    if rank and next_rank:
        span = next_rank.min_points - rank.min_points
        progress_pct = round((points - rank.min_points) / span * 100, 1) if span > 0 else 100.0
    elif rank and not next_rank:
        progress_pct = 100.0
    else:
        progress_pct = 0.0

    return UserRankResponse(
        points=points,
        rank=RankResponse.model_validate(rank) if rank else None,
        next_rank=RankResponse.model_validate(next_rank) if next_rank else None,
        progress_pct=progress_pct,
    )


@router.get("/", response_model=list[RankResponse])
def list_ranks(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[RankResponse]:
    ranks = (
        db.query(Rank)
        .filter(Rank.is_active.is_(True))
        .order_by(Rank.min_points.asc())
        .all()
    )
    return [RankResponse.model_validate(r) for r in ranks]


@router.get("/me", response_model=UserRankResponse)
def my_rank(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRankResponse:
    return _build_user_rank(db, current_user.id)


@router.get("/users/{user_id}", response_model=UserRankResponse)
def user_rank(
    user_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRankResponse:
    ensure_profile_visible(db, current_user.id, user_id)
    return _build_user_rank(db, user_id)
