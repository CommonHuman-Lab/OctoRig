# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import UTC, datetime
from typing import Any

import redis as redis_lib
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.config import settings
from app.core.exceptions import bad_request, not_found, too_many_requests
from app.models.challenge import ChallengeDifficulty, ChallengeSubmission, ChallengeType
from app.models.user import User
from app.services import audit_service
from app.services.challenge_rendering import render_target_text
from app.services.challenge_service import (
    get_challenge_by_slug_or_404,
    get_solve_count,
    get_unlocked_hint_ids,
    list_challenges,
    submit_flag,
    unlock_hint,
)
from app.services.scoring_service import (
    ScoreTransactionSource,
    award_points,
    compute_dynamic_points,
    get_user_score,
)
from app.services.settings_service import get_settings

router = APIRouter(prefix="/challenges", tags=["challenges"])

_redis: redis_lib.Redis | None = None


def _get_redis() -> redis_lib.Redis:
    global _redis
    if _redis is None:
        _redis = redis_lib.from_url(settings.redis_url, decode_responses=True)
    return _redis


# ── Rate limiting ─────────────────────────────────────────────────────────────

_RATE_LIMIT = 10
_RATE_WINDOW = 60  # seconds


def _check_submit_rate_limit(user_id: int, challenge_id: int) -> None:
    key = f"flag:ratelimit:{user_id}:{challenge_id}"
    r = _get_redis()
    count = r.incr(key)
    if count == 1:
        r.expire(key, _RATE_WINDOW)
    if count > _RATE_LIMIT:
        ttl = max(r.ttl(key), 0)
        raise too_many_requests(f"Too many attempts. Try again in {ttl} seconds.")


# ── Schemas ───────────────────────────────────────────────────────────────────


class HintResponse(BaseModel):
    id: int
    order_num: int
    cost: int
    content: str | None = None
    unlocked: bool = False

    model_config = {"from_attributes": True}


class RequiredLabSummary(BaseModel):
    slug: str
    name: str


class ChallengeListItem(BaseModel):
    id: int
    slug: str
    title: str
    difficulty: ChallengeDifficulty
    category: str
    tags: list[str]
    points: int
    challenge_type: ChallengeType
    estimated_minutes: int | None
    solve_count: int = 0
    solved_by_me: bool = False
    is_active: bool = True
    lab_slug: str | None = None
    lab_name: str | None = None
    lab_category: str | None = None
    required_labs: list[RequiredLabSummary] = []

    model_config = {"from_attributes": True}


class SetActiveRequest(BaseModel):
    is_active: bool


class ChallengeDetail(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    difficulty: ChallengeDifficulty
    category: str
    tags: list[Any]
    skills: list[Any]
    points: int
    challenge_type: ChallengeType
    estimated_minutes: int | None
    content: dict[str, Any]
    hints: list[HintResponse]
    files: list[dict[str, Any]]
    solve_count: int = 0
    solved_by_me: bool = False
    first_blood_user: str | None = None
    version: int
    lab_slug: str | None = None
    lab_name: str | None = None
    lab_category: str | None = None
    required_labs: list[RequiredLabSummary] = []

    model_config = {"from_attributes": True}


class FlagSubmitRequest(BaseModel):
    flag: str = Field(..., min_length=1, max_length=512)
    event_id: int | None = None


class FlagSubmitResponse(BaseModel):
    correct: bool
    already_solved: bool
    first_blood: bool
    points_awarded: int
    message: str


class HintUnlockResponse(BaseModel):
    hint_id: int
    content: str
    cost: int


# ── Helpers ───────────────────────────────────────────────────────────────────


def _resolve_required_labs(db: Session, slugs: list[str]) -> list[RequiredLabSummary]:
    if not slugs:
        return []
    from app.models.lab_template import LabTemplate

    rows = db.query(LabTemplate).filter(LabTemplate.slug.in_(slugs)).all()
    by_slug = {r.slug: r.name for r in rows}
    return [RequiredLabSummary(slug=s, name=by_slug.get(s, s)) for s in slugs]


def _serialize_hint(
    hint, unlocked_ids: set[int], db: Session, current_user: User, lab_template_id: int | None
) -> HintResponse:
    unlocked = hint.id in unlocked_ids
    content = hint.content if unlocked else None
    if unlocked:
        content = render_target_text(content, db, current_user, lab_template_id)
    return HintResponse(
        id=hint.id,
        order_num=hint.order_num,
        cost=hint.cost,
        content=content,
        unlocked=unlocked,
    )


def _get_team_id(db: Session, user: User) -> int | None:
    from app.models.team import TeamMember

    membership = db.query(TeamMember).filter(TeamMember.user_id == user.id).first()
    return membership.team_id if membership else None


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/", response_model=list[ChallengeListItem])
def list_challenges_endpoint(
    category: str | None = Query(None),
    difficulty: str | None = Query(None),
    search: str | None = Query(None),
    tag: str | None = Query(None),
    lab_category: str | None = Query(None, description="world | firerange | thirdparty"),
    lab_slug: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChallengeListItem]:
    from app.services.challenge_service import check_already_solved

    challenges = list_challenges(
        db,
        category=category,
        difficulty=difficulty,
        search=search,
        tag=tag,
        lab_category=lab_category,
        lab_slug=lab_slug,
    )
    items = []
    for ch in challenges:
        lab = ch.lab_template
        items.append(
            ChallengeListItem(
                id=ch.id,
                slug=ch.slug,
                title=ch.title,
                difficulty=ch.difficulty,
                category=ch.category,
                tags=ch.tags,
                points=ch.points,
                challenge_type=ch.challenge_type,
                estimated_minutes=ch.estimated_minutes,
                solve_count=get_solve_count(db, ch.id),
                solved_by_me=check_already_solved(db, ch.id, current_user.id),
                is_active=ch.is_active,
                lab_slug=lab.slug if lab else None,
                lab_name=lab.name if lab else None,
                lab_category=lab.category if lab else None,
                required_labs=_resolve_required_labs(db, ch.required_lab_slugs or []),
            )
        )
    return items


@router.get("/{slug}", response_model=ChallengeDetail)
def get_challenge_endpoint(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChallengeDetail:
    from app.services.challenge_service import check_already_solved

    ch = get_challenge_by_slug_or_404(db, slug)
    unlocked_ids = get_unlocked_hint_ids(db, current_user.id, ch.id)
    lab = ch.lab_template
    site = get_settings(db)

    first_blood_user: str | None = None
    if site.first_blood_enabled:
        fb_sub = (
            db.query(ChallengeSubmission)
            .filter(
                ChallengeSubmission.challenge_id == ch.id,
                ChallengeSubmission.is_first_blood.is_(True),
            )
            .first()
        )
        if fb_sub:
            fb_user = db.get(User, fb_sub.user_id)
            first_blood_user = fb_user.username if fb_user else None

    return ChallengeDetail(
        id=ch.id,
        slug=ch.slug,
        title=ch.title,
        description=render_target_text(ch.description, db, current_user, ch.lab_template_id),
        difficulty=ch.difficulty,
        category=ch.category,
        tags=ch.tags,
        skills=ch.skills,
        points=ch.points,
        challenge_type=ch.challenge_type,
        estimated_minutes=ch.estimated_minutes,
        content=ch.content,
        hints=[
            _serialize_hint(h, unlocked_ids, db, current_user, ch.lab_template_id) for h in ch.hints
        ],
        files=[{"id": f.id, "filename": f.filename, "size_bytes": f.size_bytes} for f in ch.files],
        solve_count=get_solve_count(db, ch.id),
        solved_by_me=check_already_solved(db, ch.id, current_user.id),
        first_blood_user=first_blood_user,
        version=ch.version,
        lab_slug=lab.slug if lab else None,
        lab_name=lab.name if lab else None,
        lab_category=lab.category if lab else None,
        required_labs=_resolve_required_labs(db, ch.required_lab_slugs or []),
    )


@router.post("/{slug}/submit", response_model=FlagSubmitResponse)
def submit_flag_endpoint(
    slug: str,
    body: FlagSubmitRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FlagSubmitResponse:
    ch = get_challenge_by_slug_or_404(db, slug)
    site = get_settings(db)

    # Max attempts enforcement (global default, applies outside events)
    if site.max_flag_attempts is not None and body.event_id is None:
        attempt_count = (
            db.query(ChallengeSubmission)
            .filter(
                ChallengeSubmission.challenge_id == ch.id,
                ChallengeSubmission.user_id == current_user.id,
                ChallengeSubmission.is_correct.is_(False),
            )
            .count()
        )
        if attempt_count >= site.max_flag_attempts:
            raise too_many_requests(f"Max attempts reached ({site.max_flag_attempts}).")

    _check_submit_rate_limit(current_user.id, ch.id)

    ip = request.client.host if request.client else None
    team_id = _get_team_id(db, current_user)

    # Count existing correct solves before submitting (for dynamic scoring)
    solve_count_before = get_solve_count(db, ch.id)

    result = submit_flag(
        db,
        challenge_id=ch.id,
        submitted_value=body.flag,
        user_id=current_user.id,
        team_id=team_id,
        event_id=body.event_id,
        ip_address=ip,
    )

    if result.already_solved:
        return FlagSubmitResponse(
            correct=True,
            already_solved=True,
            first_blood=False,
            points_awarded=0,
            message="Already solved.",
        )

    audit_service.write_audit(
        db,
        action=audit_service.CHALLENGE_SUBMITTED,
        user_id=current_user.id,
        detail={"challenge_id": ch.id, "slug": ch.slug, "correct": result.correct},
        ip=ip,
    )

    if result.correct:
        # Dynamic scoring: override points if enabled (global scoreboard only, not per-event)
        points = result.points_awarded
        if site.dynamic_scoring_enabled and body.event_id is None:
            floor = max(1, int(ch.points * site.dynamic_min_floor_pct / 100))
            points = max(
                compute_dynamic_points(ch.points, solve_count_before, site.dynamic_decay_factor),
                floor,
            )

        award_points(
            db,
            user_id=current_user.id,
            points=points,
            source_type=ScoreTransactionSource.CHALLENGE_SOLVE,
            source_id=ch.id,
            team_id=team_id,
            event_id=body.event_id,
        )
        audit_service.write_audit(
            db,
            action=audit_service.CHALLENGE_SOLVED,
            user_id=current_user.id,
            detail={
                "challenge_id": ch.id,
                "slug": ch.slug,
                "first_blood": result.first_blood,
                "points": points,
            },
            ip=ip,
        )
        msg = "First blood! " if result.first_blood else ""
        msg += f"Correct! +{points} points."
        return FlagSubmitResponse(
            correct=True,
            already_solved=False,
            first_blood=result.first_blood,
            points_awarded=points,
            message=msg,
        )

    return FlagSubmitResponse(
        correct=False,
        already_solved=False,
        first_blood=False,
        points_awarded=0,
        message="Incorrect flag.",
    )


@router.post("/{slug}/hints/{hint_id}/unlock", response_model=HintUnlockResponse)
def unlock_hint_endpoint(
    slug: str,
    hint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HintUnlockResponse:
    ch = get_challenge_by_slug_or_404(db, slug)
    hint = unlock_hint(db, hint_id, current_user.id)

    if hint.challenge_id != ch.id:
        raise not_found("Hint")

    if hint.cost > 0:
        balance = get_user_score(db, current_user.id)
        if balance < hint.cost:
            raise bad_request(f"Not enough points — hint costs {hint.cost} but you have {balance}.")
        team_id = _get_team_id(db, current_user)
        from app.services.scoring_service import deduct_hint_cost

        deduct_hint_cost(
            db, user_id=current_user.id, cost=hint.cost, hint_id=hint_id, team_id=team_id
        )

    content = render_target_text(hint.content, db, current_user, ch.lab_template_id)
    return HintUnlockResponse(hint_id=hint.id, content=content, cost=hint.cost)


# ── Admin endpoints ───────────────────────────────────────────────────────────


@router.get("/admin/all", response_model=list[ChallengeListItem])
def admin_list_challenges(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[ChallengeListItem]:
    from app.models.challenge import Challenge as Ch

    challenges = db.query(Ch).filter(Ch.is_archived.is_(False)).order_by(Ch.created_at.desc()).all()
    from app.services.challenge_service import get_solve_count

    items = []
    for ch in challenges:
        lab = ch.lab_template
        items.append(
            ChallengeListItem(
                id=ch.id,
                slug=ch.slug,
                title=ch.title,
                difficulty=ch.difficulty,
                category=ch.category,
                tags=ch.tags,
                points=ch.points,
                challenge_type=ch.challenge_type,
                estimated_minutes=ch.estimated_minutes,
                solve_count=get_solve_count(db, ch.id),
                solved_by_me=False,
                is_active=ch.is_active,
                lab_slug=lab.slug if lab else None,
                lab_name=lab.name if lab else None,
                lab_category=lab.category if lab else None,
            )
        )
    return items


@router.patch("/{slug}/active")
def set_challenge_active(
    slug: str,
    body: SetActiveRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    from app.models.challenge import Challenge as Ch

    ch = db.query(Ch).filter(Ch.slug == slug).first()
    if ch is None:
        raise not_found("Challenge")
    ch.is_active = body.is_active
    ch.updated_at = datetime.now(UTC)
    db.commit()
    return {"slug": ch.slug, "is_active": ch.is_active}
