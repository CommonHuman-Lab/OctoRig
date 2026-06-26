# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import re

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.note import Note
from app.models.user import User
from app.services.note_service import create_note, delete_note, get_note, list_notes, update_note

router = APIRouter(prefix="/notes", tags=["notes"])


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    lab_template_id: int | None
    challenge_id: int | None
    visibility: str
    team_id: int | None
    owner_id: int
    created_at: str
    updated_at: str

    @classmethod
    def from_model(cls, note: Note) -> "NoteResponse":
        return cls(
            id=note.id,
            title=note.title,
            content=note.content,
            tags=list(note.tags or []),
            lab_template_id=note.lab_template_id,
            challenge_id=note.challenge_id,
            visibility=note.visibility.value,
            team_id=note.team_id,
            owner_id=note.owner_id,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat(),
        )


class NoteCreateRequest(BaseModel):
    title: str
    content: str = ""
    tags: list[str] = []
    lab_template_id: int | None = None
    challenge_id: int | None = None
    visibility: str = "private"
    team_id: int | None = None


class NoteUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    lab_template_id: int | None = None
    challenge_id: int | None = None
    visibility: str | None = None
    team_id: int | None = None


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    return slug.strip("-")[:64] or "note"


@router.get("", response_model=list[NoteResponse])
def get_notes(
    lab_template_id: int | None = None,
    challenge_id: int | None = None,
    tag: str | None = None,
    q: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NoteResponse]:
    notes = list_notes(
        db, current_user, lab_template_id=lab_template_id, challenge_id=challenge_id, tag=tag, q=q
    )
    return [NoteResponse.from_model(n) for n in notes]


@router.post("", response_model=NoteResponse)
def post_note(
    body: NoteCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteResponse:
    note = create_note(
        db,
        current_user,
        title=body.title,
        content=body.content,
        tags=body.tags,
        lab_template_id=body.lab_template_id,
        challenge_id=body.challenge_id,
        visibility=body.visibility,
        team_id=body.team_id,
    )
    return NoteResponse.from_model(note)


@router.get("/{note_id}", response_model=NoteResponse)
def get_note_by_id(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteResponse:
    return NoteResponse.from_model(get_note(db, current_user, note_id))


@router.patch("/{note_id}", response_model=NoteResponse)
def patch_note(
    note_id: int,
    body: NoteUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteResponse:
    note = update_note(
        db,
        current_user,
        note_id,
        title=body.title,
        content=body.content,
        tags=body.tags,
        lab_template_id=body.lab_template_id,
        challenge_id=body.challenge_id,
        visibility=body.visibility,
        team_id=body.team_id,
    )
    return NoteResponse.from_model(note)


@router.delete("/{note_id}", status_code=204)
def remove_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_note(db, current_user, note_id)


@router.get("/{note_id}/export")
def export_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    note = get_note(db, current_user, note_id)
    body = f"# {note.title}\n\n"
    if note.tags:
        body += f"_Tags: {', '.join(note.tags)}_\n\n"
    body += note.content
    filename = f"{_slugify(note.title)}.md"
    return Response(
        content=body,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
