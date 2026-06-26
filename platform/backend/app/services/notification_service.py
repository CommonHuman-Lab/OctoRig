# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationPreference


def create_notification(
    db: Session,
    user_id: int,
    type: str,
    title: str,
    body: str | None = None,
    data: dict[str, Any] | None = None,
) -> Notification:
    prefs = _get_prefs(db, user_id)
    if prefs.event_filter.get(type) is False:
        return None  # type: ignore[return-value]
    if not prefs.in_app:
        return None  # type: ignore[return-value]

    n = Notification(
        user_id=user_id,
        type=type,
        title=title,
        body=body,
        data=data or {},
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def list_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    limit: int = 50,
) -> list[Notification]:
    q = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        q = q.filter(Notification.read_at.is_(None))
    return q.order_by(Notification.created_at.desc()).limit(limit).all()


def mark_read(db: Session, user_id: int, notification_id: int) -> Notification | None:
    n = db.get(Notification, notification_id)
    if n is None or n.user_id != user_id:
        return None
    n.read_at = datetime.now(UTC)
    db.commit()
    return n


def mark_all_read(db: Session, user_id: int) -> int:
    now = datetime.now(UTC)
    updated = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
        .all()
    )
    for n in updated:
        n.read_at = now
    db.commit()
    return len(updated)


def unread_count(db: Session, user_id: int) -> int:
    from sqlalchemy import func

    return (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
        .scalar()
        or 0
    )


def _get_prefs(db: Session, user_id: int) -> NotificationPreference:
    prefs = (
        db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
    )
    if prefs is None:
        prefs = NotificationPreference(user_id=user_id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


def get_preferences(db: Session, user_id: int) -> NotificationPreference:
    return _get_prefs(db, user_id)


def update_preferences(
    db: Session,
    user_id: int,
    in_app: bool | None = None,
    email: bool | None = None,
    discord_webhook_url: str | None = None,
    slack_webhook_url: str | None = None,
    event_filter: dict[str, Any] | None = None,
) -> NotificationPreference:
    prefs = _get_prefs(db, user_id)
    if in_app is not None:
        prefs.in_app = in_app
    if email is not None:
        prefs.email = email
    if discord_webhook_url is not None:
        prefs.discord_webhook_url = discord_webhook_url
    if slack_webhook_url is not None:
        prefs.slack_webhook_url = slack_webhook_url
    if event_filter is not None:
        prefs.event_filter = event_filter
    db.commit()
    db.refresh(prefs)
    return prefs
