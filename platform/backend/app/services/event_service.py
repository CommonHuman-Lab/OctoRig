# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import bad_request, conflict, not_found
from app.models.challenge import Challenge, ChallengeSubmission
from app.models.ctf_event import (
    CtfEvent, EventChallengeMap, EventRegistration, EventStatus, EventVisibility,
)
from app.models.scoring import ScoreTransaction
from app.models.team import Team, TeamMember
from app.services.scoring_service import compute_dynamic_points


# ── Read ──────────────────────────────────────────────────────────────────────

def get_event_or_404(db: Session, event_id: int) -> CtfEvent:
    ev = db.get(CtfEvent, event_id)
    if ev is None:
        raise not_found("Event")
    return ev


def get_event_by_slug_or_404(db: Session, slug: str) -> CtfEvent:
    ev = db.query(CtfEvent).filter(CtfEvent.slug == slug).first()
    if ev is None:
        raise not_found("Event")
    return ev


def check_event_visible(ev: CtfEvent, user, db: Session) -> None:
    """Raise not_found if a non-privileged user shouldn't be able to see this event.

    Mirrors the filtering list_events() applies, but for a single already-loaded event.
    """
    from app.core.permissions import is_privileged

    if is_privileged(user, db):
        return
    if ev.status == EventStatus.ARCHIVED or ev.visibility == EventVisibility.PRIVATE:
        raise not_found("Event")


def get_visible_event_or_404(db: Session, slug: str, user) -> CtfEvent:
    ev = get_event_by_slug_or_404(db, slug)
    check_event_visible(ev, user, db)
    return ev


def list_events(
    db: Session,
    status: Optional[str] = None,
    visibility: Optional[str] = None,
    include_private: bool = False,
) -> list[CtfEvent]:
    q = db.query(CtfEvent).filter(CtfEvent.status != EventStatus.ARCHIVED)
    if not include_private:
        q = q.filter(CtfEvent.visibility != EventVisibility.PRIVATE)
    if status:
        q = q.filter(CtfEvent.status == status)
    if visibility:
        q = q.filter(CtfEvent.visibility == visibility)
    return q.order_by(CtfEvent.created_at.desc()).all()


# ── Lifecycle ─────────────────────────────────────────────────────────────────

_VALID_TRANSITIONS: dict[EventStatus, list[EventStatus]] = {
    EventStatus.DRAFT:      [EventStatus.PUBLISHED],
    EventStatus.PUBLISHED:  [EventStatus.RUNNING, EventStatus.DRAFT],
    EventStatus.RUNNING:    [EventStatus.ENDED],
    EventStatus.ENDED:      [EventStatus.ARCHIVED],
    EventStatus.ARCHIVED:   [],
}


def transition_status(db: Session, event: CtfEvent, new_status: EventStatus) -> CtfEvent:
    allowed = _VALID_TRANSITIONS.get(event.status, [])
    if new_status not in allowed:
        raise bad_request(
            f"Cannot transition from '{event.status}' to '{new_status}'. "
            f"Allowed: {[s.value for s in allowed] or 'none'}"
        )
    event.status = new_status
    db.commit()
    db.refresh(event)
    return event


# ── Challenge management ──────────────────────────────────────────────────────

def add_challenge(
    db: Session,
    event: CtfEvent,
    challenge_id: int,
    points_override: Optional[int] = None,
    released_at: Optional[datetime] = None,
) -> EventChallengeMap:
    challenge = db.get(Challenge, challenge_id)
    if challenge is None or challenge.is_archived:
        raise not_found("Challenge")

    existing = (
        db.query(EventChallengeMap)
        .filter(
            EventChallengeMap.event_id == event.id,
            EventChallengeMap.challenge_id == challenge_id,
        )
        .first()
    )
    if existing:
        raise conflict("Challenge already in event")

    ecm = EventChallengeMap(
        event_id=event.id,
        challenge_id=challenge_id,
        points_override=points_override,
        released_at=released_at,
    )
    db.add(ecm)
    db.commit()
    db.refresh(ecm)
    return ecm


def remove_challenge(db: Session, event: CtfEvent, challenge_id: int) -> None:
    ecm = (
        db.query(EventChallengeMap)
        .filter(
            EventChallengeMap.event_id == event.id,
            EventChallengeMap.challenge_id == challenge_id,
        )
        .first()
    )
    if ecm is None:
        raise not_found("Challenge in event")
    db.delete(ecm)
    db.commit()


def get_event_challenges(
    db: Session,
    event: CtfEvent,
    user_id: Optional[int] = None,
) -> list[dict]:
    now = datetime.now(timezone.utc)
    maps = db.query(EventChallengeMap).filter(
        EventChallengeMap.event_id == event.id
    ).all()

    solved_ids: set[int] = set()
    if user_id is not None:
        rows = (
            db.query(ChallengeSubmission.challenge_id)
            .filter(
                ChallengeSubmission.event_id == event.id,
                ChallengeSubmission.user_id == user_id,
                ChallengeSubmission.is_correct.is_(True),
            )
            .all()
        )
        solved_ids = {r.challenge_id for r in rows}

    result = []
    for ecm in maps:
        if ecm.released_at and ecm.released_at > now:
            continue
        ch = ecm.challenge
        solve_count = (
            db.query(func.count(ChallengeSubmission.id))
            .filter(
                ChallengeSubmission.challenge_id == ch.id,
                ChallengeSubmission.event_id == event.id,
                ChallengeSubmission.is_correct.is_(True),
            )
            .scalar() or 0
        )
        base_pts = ecm.points_override or ch.points
        if event.scoring_mode.value == "dynamic":
            pts = compute_dynamic_points(base_pts, solve_count)
        else:
            pts = base_pts

        result.append({
            "id": ch.id,
            "slug": ch.slug,
            "title": ch.title,
            "category": ch.category,
            "difficulty": ch.difficulty.value,
            "points": pts,
            "tags": ch.tags,
            "solve_count": solve_count,
            "solved_by_me": ch.id in solved_ids,
            "released_at": ecm.released_at.isoformat() if ecm.released_at else None,
        })

    return result


# ── Registration ──────────────────────────────────────────────────────────────

def register_team(db: Session, event: CtfEvent, team_id: int) -> EventRegistration:
    if event.status not in (EventStatus.PUBLISHED, EventStatus.RUNNING):
        raise bad_request("Registration is only open for published or running events")

    team = db.get(Team, team_id)
    if team is None:
        raise not_found("Team")

    if event.max_team_size:
        member_count = (
            db.query(func.count(TeamMember.id))
            .filter(TeamMember.team_id == team_id)
            .scalar() or 0
        )
        if member_count > event.max_team_size:
            raise bad_request(
                f"Team size ({member_count}) exceeds event limit ({event.max_team_size})"
            )

    existing = (
        db.query(EventRegistration)
        .filter(EventRegistration.event_id == event.id, EventRegistration.team_id == team_id)
        .first()
    )
    if existing:
        raise conflict("Team already registered for this event")

    reg = EventRegistration(event_id=event.id, team_id=team_id)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def unregister_team(db: Session, event: CtfEvent, team_id: int) -> None:
    if event.status == EventStatus.RUNNING:
        raise bad_request("Cannot unregister from a running event")

    reg = (
        db.query(EventRegistration)
        .filter(EventRegistration.event_id == event.id, EventRegistration.team_id == team_id)
        .first()
    )
    if reg is None:
        raise not_found("Registration")
    db.delete(reg)
    db.commit()


# ── Scoreboard freeze ─────────────────────────────────────────────────────────

def is_scoreboard_frozen(event: CtfEvent) -> bool:
    if event.freeze_scoreboard_at is None:
        return False
    return datetime.now(timezone.utc) >= event.freeze_scoreboard_at
