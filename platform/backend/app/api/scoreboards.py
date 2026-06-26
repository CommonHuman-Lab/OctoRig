# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.pagination import WideLimit
from app.models.user import User
from app.services.event_service import check_event_visible, get_event_or_404
from app.services.profile_service import ensure_profile_visible
from app.services.scoring_service import (
    get_event_scoreboard,
    get_global_scoreboard,
    get_user_score,
)

router = APIRouter(prefix="/scoreboards", tags=["scoreboards"])


class ScoreboardEntry(BaseModel):
    rank: int
    user_id: int | None = None
    username: str | None = None
    team_id: int | None = None
    total: int
    solve_count: int = 0
    badge_count: int = 0
    last_tx: str | None = None


class UserScoreResponse(BaseModel):
    user_id: int
    total: int
    event_id: int | None = None


@router.get("/global", response_model=list[ScoreboardEntry])
def global_scoreboard(
    limit: WideLimit = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ScoreboardEntry]:
    rows = get_global_scoreboard(db, limit=limit)
    return [ScoreboardEntry(**r) for r in rows]


@router.get("/events/{event_id}", response_model=list[ScoreboardEntry])
def event_scoreboard(
    event_id: int,
    limit: WideLimit = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScoreboardEntry]:
    ev = get_event_or_404(db, event_id)
    check_event_visible(ev, current_user, db)
    rows = get_event_scoreboard(db, event_id=event_id, limit=limit)
    return [ScoreboardEntry(**r) for r in rows]


@router.get("/users/{user_id}", response_model=UserScoreResponse)
def user_score(
    user_id: int,
    event_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserScoreResponse:
    ensure_profile_visible(db, current_user.id, user_id)
    total = get_user_score(db, user_id=user_id, event_id=event_id)
    return UserScoreResponse(user_id=user_id, total=total, event_id=event_id)
