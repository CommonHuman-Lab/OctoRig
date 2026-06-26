# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import json
import math
from datetime import UTC, datetime
from typing import Any

import redis as redis_lib
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models.badge import UserBadge
from app.models.challenge import ChallengeSubmission
from app.models.scoring import ScoreTransaction, ScoreTransactionSource
from app.models.user import User

_redis: redis_lib.Redis | None = None


def _get_redis() -> redis_lib.Redis:
    global _redis
    if _redis is None:
        _redis = redis_lib.from_url(settings.redis_url, decode_responses=True)
    return _redis


def award_points(
    db: Session,
    user_id: int,
    points: int,
    source_type: ScoreTransactionSource,
    source_id: int | None = None,
    team_id: int | None = None,
    event_id: int | None = None,
) -> ScoreTransaction:
    tx = ScoreTransaction(
        user_id=user_id,
        team_id=team_id,
        event_id=event_id,
        source_type=source_type,
        source_id=source_id,
        points=points,
    )
    db.add(tx)
    db.commit()
    _invalidate_scoreboard_cache(event_id)
    return tx


def deduct_hint_cost(
    db: Session,
    user_id: int,
    cost: int,
    hint_id: int,
    team_id: int | None = None,
    event_id: int | None = None,
) -> ScoreTransaction | None:
    if cost <= 0:
        return None
    return award_points(
        db,
        user_id=user_id,
        points=-cost,
        source_type=ScoreTransactionSource.HINT_COST,
        source_id=hint_id,
        team_id=team_id,
        event_id=event_id,
    )


def get_user_score(db: Session, user_id: int, event_id: int | None = None) -> int:
    q = db.query(func.coalesce(func.sum(ScoreTransaction.points), 0)).filter(
        ScoreTransaction.user_id == user_id
    )
    if event_id is not None:
        q = q.filter(ScoreTransaction.event_id == event_id)
    return int(q.scalar() or 0)


def get_global_scoreboard(db: Session, limit: int = 100) -> list[dict[str, Any]]:
    from app.services.settings_service import get_settings

    site = get_settings(db)
    freeze_at = site.scoreboard_frozen_at
    now = datetime.now(UTC)
    frozen = freeze_at is not None and freeze_at.replace(tzinfo=UTC) <= now

    cache_key = f"scoreboard:global:{limit}:{'frozen' if frozen else 'live'}"
    cached = _get_redis().get(cache_key)
    if cached:
        return json.loads(cached)

    q = db.query(
        ScoreTransaction.user_id,
        func.sum(ScoreTransaction.points).label("total"),
        func.max(ScoreTransaction.created_at).label("last_tx"),
    ).filter(ScoreTransaction.event_id.is_(None))
    if frozen:
        q = q.filter(ScoreTransaction.created_at <= freeze_at)
    score_rows = (
        q.group_by(ScoreTransaction.user_id)
        .order_by(
            func.sum(ScoreTransaction.points).desc(),
            func.max(ScoreTransaction.created_at).asc(),
        )
        .limit(limit)
        .all()
    )

    user_ids = [r.user_id for r in score_rows]

    usernames: dict[int, str] = {
        u.id: u.username for u in db.query(User).filter(User.id.in_(user_ids)).all()
    }
    solve_counts: dict[int, int] = {
        row[0]: int(row[1])
        for row in db.query(
            ChallengeSubmission.user_id,
            func.count(ChallengeSubmission.id),
        )
        .filter(
            ChallengeSubmission.user_id.in_(user_ids),
            ChallengeSubmission.is_correct.is_(True),
        )
        .group_by(ChallengeSubmission.user_id)
        .all()
    }
    badge_counts: dict[int, int] = {
        row[0]: int(row[1])
        for row in db.query(
            UserBadge.user_id,
            func.count(UserBadge.id),
        )
        .filter(UserBadge.user_id.in_(user_ids))
        .group_by(UserBadge.user_id)
        .all()
    }

    result = [
        {
            "rank": idx + 1,
            "user_id": r.user_id,
            "username": usernames.get(r.user_id),
            "total": int(r.total or 0),
            "solve_count": solve_counts.get(r.user_id, 0),
            "badge_count": badge_counts.get(r.user_id, 0),
            "last_tx": r.last_tx.isoformat() if r.last_tx else None,
            "frozen": frozen,
        }
        for idx, r in enumerate(score_rows)
    ]
    _get_redis().setex(cache_key, 5, json.dumps(result))
    return result


def get_event_scoreboard(db: Session, event_id: int, limit: int = 100) -> list[dict[str, Any]]:
    cache_key = f"scoreboard:event:{event_id}"
    cached = _get_redis().get(cache_key)
    if cached:
        return json.loads(cached)

    rows = (
        db.query(
            ScoreTransaction.team_id,
            func.sum(ScoreTransaction.points).label("total"),
            func.max(ScoreTransaction.created_at).label("last_tx"),
        )
        .filter(ScoreTransaction.event_id == event_id, ScoreTransaction.team_id.isnot(None))
        .group_by(ScoreTransaction.team_id)
        .order_by(
            func.sum(ScoreTransaction.points).desc(),
            func.max(ScoreTransaction.created_at).asc(),
        )
        .limit(limit)
        .all()
    )
    result = [
        {
            "rank": idx + 1,
            "team_id": r.team_id,
            "total": int(r.total or 0),
            "last_tx": r.last_tx.isoformat() if r.last_tx else None,
        }
        for idx, r in enumerate(rows)
    ]
    _get_redis().setex(cache_key, 5, json.dumps(result))
    return result


def compute_dynamic_points(base: int, solve_count: int, decay_factor: float = 0.9) -> int:
    """Decay formula: points fall by decay_factor per additional solve, floor at 10% of base."""
    decayed = base * (decay_factor ** max(0, solve_count - 1))
    return max(math.floor(decayed), math.floor(base * 0.1))


def _invalidate_scoreboard_cache(event_id: int | None) -> None:
    r = _get_redis()
    if event_id is not None:
        r.delete(f"scoreboard:event:{event_id}")
    else:
        for suffix in ("live", "frozen"):
            r.delete(f"scoreboard:global:100:{suffix}")
