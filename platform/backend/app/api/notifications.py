# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.pagination import DefaultLimit
from app.models.user import User
from app.models.notification import Notification
from app.services.notification_service import (
    get_preferences, list_notifications, mark_all_read, mark_read,
    unread_count, update_preferences,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    body: Optional[str]
    data: dict[str, Any]
    read_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class PreferencesOut(BaseModel):
    in_app: bool
    email: bool
    discord_webhook_url: Optional[str]
    slack_webhook_url: Optional[str]
    event_filter: dict[str, Any]

    model_config = {"from_attributes": True}


class PreferencesUpdateRequest(BaseModel):
    in_app: Optional[bool] = None
    email: Optional[bool] = None
    discord_webhook_url: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    event_filter: Optional[dict[str, Any]] = None


class UnreadCountOut(BaseModel):
    count: int


class ReadResultOut(BaseModel):
    ok: bool


class MarkedCountOut(BaseModel):
    marked: int


@router.get("/", response_model=list[NotificationOut])
def list_notifications_endpoint(
    unread_only: bool = Query(False),
    limit: DefaultLimit = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NotificationOut]:
    return list_notifications(db, current_user.id, unread_only=unread_only, limit=limit)


@router.get("/unread-count", response_model=UnreadCountOut)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnreadCountOut:
    return UnreadCountOut(count=unread_count(db, current_user.id))


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    n = db.get(Notification, notification_id)
    if n is not None and n.user_id == current_user.id:
        db.delete(n)
        db.commit()


@router.post("/{notification_id}/read", response_model=ReadResultOut)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReadResultOut:
    result = mark_read(db, current_user.id, notification_id)
    return ReadResultOut(ok=result is not None)


@router.post("/read-all", response_model=MarkedCountOut)
def mark_all_read_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MarkedCountOut:
    count = mark_all_read(db, current_user.id)
    return MarkedCountOut(marked=count)


@router.get("/preferences", response_model=PreferencesOut)
def get_prefs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PreferencesOut:
    return get_preferences(db, current_user.id)


@router.patch("/preferences", response_model=PreferencesOut)
def update_prefs(
    body: PreferencesUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PreferencesOut:
    return update_preferences(
        db,
        user_id=current_user.id,
        in_app=body.in_app,
        email=body.email,
        discord_webhook_url=body.discord_webhook_url,
        slack_webhook_url=body.slack_webhook_url,
        event_filter=body.event_filter,
    )
