# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import UTC, datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exceptions import bad_request, forbidden_exception, not_found
from app.models.note import Note, NoteVisibility
from app.models.team import TeamMember
from app.models.user import User


def _user_team_ids(db: Session, user_id: int) -> list[int]:
    rows = db.query(TeamMember.team_id).filter(TeamMember.user_id == user_id).distinct().all()
    return [row[0] for row in rows]


def _resolve_team_id(
    db: Session, user: User, visibility: NoteVisibility, team_id: int | None
) -> int | None:
    if visibility == NoteVisibility.PRIVATE:
        return None
    if team_id is None:
        raise bad_request("team_id is required when visibility is 'team'")
    if team_id not in _user_team_ids(db, user.id):
        raise forbidden_exception
    return team_id


def list_notes(
    db: Session,
    user: User,
    *,
    lab_template_id: int | None = None,
    challenge_id: int | None = None,
    tag: str | None = None,
    q: str | None = None,
) -> list[Note]:
    query = db.query(Note).filter(
        or_(
            Note.owner_id == user.id,
            (Note.visibility == NoteVisibility.TEAM)
            & Note.team_id.in_(_user_team_ids(db, user.id)),
        )
    )
    if lab_template_id is not None:
        query = query.filter(Note.lab_template_id == lab_template_id)
    if challenge_id is not None:
        query = query.filter(Note.challenge_id == challenge_id)
    if tag is not None:
        query = query.filter(Note.tags.contains([tag]))
    if q:
        query = query.filter(or_(Note.title.ilike(f"%{q}%"), Note.content.ilike(f"%{q}%")))
    return query.order_by(Note.updated_at.desc()).all()


def _get_visible_note(db: Session, user: User, note_id: int) -> Note:
    note = db.get(Note, note_id)
    if note is None:
        raise not_found("Note")
    is_owner = note.owner_id == user.id
    is_shared = (
        note.visibility == NoteVisibility.TEAM
        and note.team_id is not None
        and note.team_id in _user_team_ids(db, user.id)
    )
    if not is_owner and not is_shared:
        raise not_found("Note")
    return note


def get_note(db: Session, user: User, note_id: int) -> Note:
    return _get_visible_note(db, user, note_id)


def create_note(
    db: Session,
    user: User,
    *,
    title: str,
    content: str = "",
    tags: list[str] | None = None,
    lab_template_id: int | None = None,
    challenge_id: int | None = None,
    visibility: str = NoteVisibility.PRIVATE.value,
    team_id: int | None = None,
) -> Note:
    resolved_visibility = NoteVisibility(visibility)
    note = Note(
        owner_id=user.id,
        title=title,
        content=content,
        tags=tags or [],
        lab_template_id=lab_template_id,
        challenge_id=challenge_id,
        visibility=resolved_visibility,
        team_id=_resolve_team_id(db, user, resolved_visibility, team_id),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def update_note(
    db: Session,
    user: User,
    note_id: int,
    *,
    title: str | None = None,
    content: str | None = None,
    tags: list[str] | None = None,
    lab_template_id: int | None = None,
    challenge_id: int | None = None,
    visibility: str | None = None,
    team_id: int | None = None,
) -> Note:
    note = _get_visible_note(db, user, note_id)
    if note.owner_id != user.id:
        raise forbidden_exception
    if title is not None:
        note.title = title
    if content is not None:
        note.content = content
    if tags is not None:
        note.tags = tags
    if lab_template_id is not None:
        note.lab_template_id = lab_template_id
    if challenge_id is not None:
        note.challenge_id = challenge_id
    if visibility is not None:
        resolved_visibility = NoteVisibility(visibility)
        note.visibility = resolved_visibility
        note.team_id = _resolve_team_id(
            db, user, resolved_visibility, team_id if team_id is not None else note.team_id
        )
    elif team_id is not None:
        note.team_id = _resolve_team_id(db, user, note.visibility, team_id)
    note.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, user: User, note_id: int) -> None:
    note = _get_visible_note(db, user, note_id)
    if note.owner_id != user.id:
        raise forbidden_exception
    db.delete(note)
    db.commit()
