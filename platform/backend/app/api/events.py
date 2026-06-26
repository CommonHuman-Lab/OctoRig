# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.core.exceptions import forbidden_exception, not_found
from app.core.pagination import WideLimit
from app.core.permissions import is_privileged, role_gte
from app.models.ctf_event import EventScoringMode, EventStatus, EventVisibility
from app.models.team import TeamMember, TeamRole
from app.models.user import User
from app.services import audit_service
from app.services.event_service import (
    add_challenge,
    get_event_by_slug_or_404,
    get_event_challenges,
    get_visible_event_or_404,
    is_scoreboard_frozen,
    list_events,
    register_team,
    remove_challenge,
    transition_status,
    unregister_team,
)
from app.services.scoring_service import get_event_scoreboard

router = APIRouter(prefix="/events", tags=["events"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class EventSummary(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None
    status: EventStatus
    visibility: EventVisibility
    scoring_mode: EventScoringMode
    start_at: datetime | None
    end_at: datetime | None
    max_team_size: int | None
    freeze_scoreboard_at: datetime | None
    created_at: datetime
    scoreboard_frozen: bool = False

    model_config = {"from_attributes": True}


class EventCreateRequest(BaseModel):
    slug: str
    title: str
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    visibility: EventVisibility = EventVisibility.PRIVATE
    scoring_mode: EventScoringMode = EventScoringMode.STATIC
    max_team_size: int | None = None
    freeze_scoreboard_at: datetime | None = None


class EventUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    visibility: EventVisibility | None = None
    max_team_size: int | None = None
    freeze_scoreboard_at: datetime | None = None


class AddChallengeRequest(BaseModel):
    challenge_id: int
    points_override: int | None = None
    released_at: datetime | None = None


class RegisterTeamRequest(BaseModel):
    team_id: int


class TransitionRequest(BaseModel):
    status: EventStatus


class ScoreboardEntry(BaseModel):
    rank: int
    user_id: int | None = None
    team_id: int | None = None
    total: int
    last_tx: str | None = None


def _serialize(ev) -> EventSummary:
    return EventSummary(
        id=ev.id,
        slug=ev.slug,
        title=ev.title,
        description=ev.description,
        status=ev.status,
        visibility=ev.visibility,
        scoring_mode=ev.scoring_mode,
        start_at=ev.start_at,
        end_at=ev.end_at,
        max_team_size=ev.max_team_size,
        freeze_scoreboard_at=ev.freeze_scoreboard_at,
        created_at=ev.created_at,
        scoreboard_frozen=is_scoreboard_frozen(ev),
    )


# ── Public / authenticated endpoints ─────────────────────────────────────────

@router.get("/", response_model=list[EventSummary])
def list_events_endpoint(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EventSummary]:
    include_private = is_privileged(current_user, db)
    events = list_events(db, status=status, include_private=include_private)
    return [_serialize(ev) for ev in events]


@router.get("/{slug}", response_model=EventSummary)
def get_event_endpoint(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventSummary:
    ev = get_visible_event_or_404(db, slug, current_user)
    return _serialize(ev)


@router.get("/{slug}/challenges", response_model=list[dict[str, Any]])
def get_event_challenges_endpoint(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    ev = get_visible_event_or_404(db, slug, current_user)
    return get_event_challenges(db, ev, user_id=current_user.id)


@router.get("/{slug}/scoreboard", response_model=list[ScoreboardEntry])
def event_scoreboard_endpoint(
    slug: str,
    limit: WideLimit = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScoreboardEntry]:
    ev = get_visible_event_or_404(db, slug, current_user)
    rows = get_event_scoreboard(db, event_id=ev.id, limit=limit)
    return [ScoreboardEntry(**r) for r in rows]


def _get_membership(db: Session, user: User, team_id: int) -> TeamMember | None:
    return (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.user_id == user.id)
        .first()
    )


@router.post("/{slug}/register", response_model=dict[str, Any])
def register_endpoint(
    slug: str,
    body: RegisterTeamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    ev = get_event_by_slug_or_404(db, slug)
    membership = _get_membership(db, current_user, body.team_id)
    if membership is None and not is_privileged(current_user, db):
        raise not_found("Team")
    if not role_gte(membership, TeamRole.MEMBER) and not is_privileged(current_user, db):
        raise forbidden_exception
    reg = register_team(db, ev, body.team_id)
    return {"event_id": ev.id, "team_id": reg.team_id, "registered_at": reg.registered_at.isoformat()}


@router.delete("/{slug}/register/{team_id}", status_code=204)
def unregister_endpoint(
    slug: str,
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    ev = get_event_by_slug_or_404(db, slug)
    membership = _get_membership(db, current_user, team_id)
    if membership is None and not is_privileged(current_user, db):
        raise not_found("Team")
    if not role_gte(membership, TeamRole.MANAGER) and not is_privileged(current_user, db):
        raise forbidden_exception
    unregister_team(db, ev, team_id)


# ── Admin-only endpoints ──────────────────────────────────────────────────────

@router.post("/", response_model=EventSummary, dependencies=[Depends(require_admin)])
def create_event_endpoint(
    body: EventCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventSummary:
    from app.models.ctf_event import CtfEvent
    ev = CtfEvent(
        slug=body.slug,
        title=body.title,
        description=body.description,
        start_at=body.start_at,
        end_at=body.end_at,
        visibility=body.visibility,
        scoring_mode=body.scoring_mode,
        max_team_size=body.max_team_size,
        freeze_scoreboard_at=body.freeze_scoreboard_at,
        created_by_id=current_user.id,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    audit_service.write_audit(db, "event.created", user_id=current_user.id, detail={"slug": ev.slug})
    return _serialize(ev)


@router.patch("/{slug}", response_model=EventSummary, dependencies=[Depends(require_admin)])
def update_event_endpoint(
    slug: str,
    body: EventUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> EventSummary:
    ev = get_event_by_slug_or_404(db, slug)
    if body.title is not None:
        ev.title = body.title
    if body.description is not None:
        ev.description = body.description
    if body.start_at is not None:
        ev.start_at = body.start_at
    if body.end_at is not None:
        ev.end_at = body.end_at
    if body.visibility is not None:
        ev.visibility = body.visibility
    if body.max_team_size is not None:
        ev.max_team_size = body.max_team_size
    if body.freeze_scoreboard_at is not None:
        ev.freeze_scoreboard_at = body.freeze_scoreboard_at
    db.commit()
    db.refresh(ev)
    return _serialize(ev)


@router.post("/{slug}/status", response_model=EventSummary, dependencies=[Depends(require_admin)])
def transition_status_endpoint(
    slug: str,
    body: TransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventSummary:
    ev = get_event_by_slug_or_404(db, slug)
    ev = transition_status(db, ev, body.status)
    audit_service.write_audit(
        db, "event.status_changed",
        user_id=current_user.id,
        detail={"slug": ev.slug, "new_status": ev.status.value},
    )
    return _serialize(ev)


@router.post("/{slug}/challenges", response_model=dict[str, Any], dependencies=[Depends(require_admin)])
def add_challenge_endpoint(
    slug: str,
    body: AddChallengeRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict[str, Any]:
    ev = get_event_by_slug_or_404(db, slug)
    ecm = add_challenge(db, ev, body.challenge_id, body.points_override, body.released_at)
    return {
        "event_id": ev.id,
        "challenge_id": ecm.challenge_id,
        "points_override": ecm.points_override,
        "released_at": ecm.released_at.isoformat() if ecm.released_at else None,
    }


@router.delete("/{slug}/challenges/{challenge_id}", status_code=204, dependencies=[Depends(require_admin)])
def remove_challenge_endpoint(
    slug: str,
    challenge_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> None:
    ev = get_event_by_slug_or_404(db, slug)
    remove_challenge(db, ev, challenge_id)
