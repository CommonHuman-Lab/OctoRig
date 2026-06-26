# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_types import EnumCol as SQLEnum
from app.database import Base

if TYPE_CHECKING:
    from app.models.challenge import Challenge, ChallengeSubmission
    from app.models.scoring import ScoreTransaction
    from app.models.team import Team
    from app.models.user import User


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    RUNNING = "running"
    ENDED = "ended"
    ARCHIVED = "archived"


class EventVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class EventScoringMode(str, enum.Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"


class CtfEvent(Base):
    __tablename__ = "ctf_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[EventStatus] = mapped_column(
        SQLEnum(EventStatus), nullable=False, default=EventStatus.DRAFT, index=True
    )
    visibility: Mapped[EventVisibility] = mapped_column(
        SQLEnum(EventVisibility), nullable=False, default=EventVisibility.PRIVATE
    )
    max_team_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scoring_mode: Mapped[EventScoringMode] = mapped_column(
        SQLEnum(EventScoringMode), nullable=False, default=EventScoringMode.STATIC
    )
    freeze_scoreboard_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])
    challenge_map: Mapped[list["EventChallengeMap"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    registrations: Mapped[list["EventRegistration"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    submissions: Mapped[list["ChallengeSubmission"]] = relationship(back_populates="event")
    score_transactions: Mapped[list["ScoreTransaction"]] = relationship(back_populates="event")


class EventChallengeMap(Base):
    __tablename__ = "event_challenge_map"
    __table_args__ = (
        UniqueConstraint("event_id", "challenge_id", name="uq_event_challenge_map"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("ctf_events.id"), nullable=False, index=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"), nullable=False)
    points_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    event: Mapped["CtfEvent"] = relationship(back_populates="challenge_map")
    challenge: Mapped["Challenge"] = relationship()


class EventRegistration(Base):
    __tablename__ = "event_registrations"
    __table_args__ = (
        UniqueConstraint("event_id", "team_id", name="uq_event_registrations"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("ctf_events.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    event: Mapped["CtfEvent"] = relationship(back_populates="registrations")
    team: Mapped["Team"] = relationship()
