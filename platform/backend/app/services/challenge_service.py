# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import not_found
from app.models.challenge import (
    Challenge,
    ChallengeHint,
    ChallengeSubmission,
    HintUnlock,
)
from app.models.deployment import Deployment
from app.services.flag_service import (
    FlagContext,
    ValidationResult,
    check_already_solved,
    check_first_blood,
    validate_flag,
)


def get_challenge_or_404(db: Session, challenge_id: int) -> Challenge:
    ch = db.get(Challenge, challenge_id)
    if ch is None or not ch.is_active or ch.is_archived:
        raise not_found("Challenge")
    return ch


def get_challenge_by_slug_or_404(db: Session, slug: str) -> Challenge:
    ch = db.query(Challenge).filter(Challenge.slug == slug, Challenge.is_active.is_(True)).first()
    if ch is None or ch.is_archived:
        raise not_found("Challenge")
    return ch


def list_challenges(
    db: Session,
    category: str | None = None,
    difficulty: str | None = None,
    search: str | None = None,
    tag: str | None = None,
    lab_category: str | None = None,
    lab_slug: str | None = None,
) -> list[Challenge]:
    from app.models.lab_template import LabTemplate

    q = db.query(Challenge).filter(
        Challenge.is_active.is_(True),
        Challenge.is_archived.is_(False),
    )
    if category:
        q = q.filter(Challenge.category == category)
    if difficulty:
        q = q.filter(Challenge.difficulty == difficulty)
    if search:
        term = f"%{search}%"
        q = q.filter(Challenge.title.ilike(term) | Challenge.description.ilike(term))
    if tag:
        q = q.filter(Challenge.tags.contains([tag]))
    if lab_category or lab_slug:
        q = q.join(LabTemplate, Challenge.lab_template_id == LabTemplate.id)
        if lab_category:
            q = q.filter(LabTemplate.category == lab_category)
        if lab_slug:
            q = q.filter(LabTemplate.slug == lab_slug)
    return q.order_by(Challenge.difficulty, Challenge.points, Challenge.id).all()


def submit_flag(
    db: Session,
    challenge_id: int,
    submitted_value: str,
    user_id: int,
    team_id: int | None,
    event_id: int | None,
    ip_address: str | None,
) -> ValidationResult:
    challenge = get_challenge_or_404(db, challenge_id)

    if check_already_solved(db, challenge_id, user_id):
        return ValidationResult(correct=True, already_solved=True)

    deployment: Deployment | None = None
    if any(f.flag_type == "dynamic" for f in challenge.flags):
        deployment = (
            db.query(Deployment)
            .filter(
                Deployment.challenge_id == challenge_id,
                Deployment.instance_for_user_id == user_id,
                Deployment.dynamic_flag.isnot(None),
            )
            .first()
        )

    context = FlagContext(
        user_id=user_id,
        team_id=team_id,
        event_id=event_id,
        deployment=deployment,
    )
    result = validate_flag(challenge, submitted_value, context)

    is_first = False
    points = 0
    if result.correct:
        is_first = check_first_blood(db, challenge_id, event_id)
        points = challenge.points

    submission = ChallengeSubmission(
        challenge_id=challenge_id,
        user_id=user_id,
        team_id=team_id,
        event_id=event_id,
        submitted_value=submitted_value,
        is_correct=result.correct,
        is_first_blood=is_first,
        points_awarded=points,
        ip_address=ip_address,
        submitted_at=datetime.now(UTC),
    )
    db.add(submission)
    db.commit()

    return ValidationResult(
        correct=result.correct,
        already_solved=False,
        first_blood=is_first,
        points_awarded=points,
    )


def unlock_hint(db: Session, hint_id: int, user_id: int) -> ChallengeHint:
    hint = db.get(ChallengeHint, hint_id)
    if hint is None:
        raise not_found("Hint")

    existing = (
        db.query(HintUnlock)
        .filter(HintUnlock.hint_id == hint_id, HintUnlock.user_id == user_id)
        .first()
    )
    if existing:
        return hint

    unlock = HintUnlock(hint_id=hint_id, user_id=user_id)
    db.add(unlock)
    db.commit()
    return hint


def get_unlocked_hint_ids(db: Session, user_id: int, challenge_id: int) -> set[int]:
    rows = (
        db.query(HintUnlock.hint_id)
        .join(ChallengeHint, HintUnlock.hint_id == ChallengeHint.id)
        .filter(ChallengeHint.challenge_id == challenge_id, HintUnlock.user_id == user_id)
        .all()
    )
    return {r.hint_id for r in rows}


def get_solve_count(db: Session, challenge_id: int, event_id: int | None = None) -> int:
    q = db.query(func.count(ChallengeSubmission.id)).filter(
        ChallengeSubmission.challenge_id == challenge_id,
        ChallengeSubmission.is_correct.is_(True),
    )
    if event_id is not None:
        q = q.filter(ChallengeSubmission.event_id == event_id)
    return q.scalar() or 0
