# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
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
    from app.models.ctf_event import CtfEvent
    from app.models.deployment import Deployment
    from app.models.lab_template import LabTemplate
    from app.models.team import Team
    from app.models.user import User


class ChallengeType(str, enum.Enum):
    FLAG = "flag"
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    FILE_UPLOAD = "file_upload"
    DYNAMIC_FLAG = "dynamic_flag"
    API = "api"
    WEB = "web"
    CONTAINER = "container"


class ChallengeDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    INSANE = "insane"


class FlagType(str, enum.Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    PER_USER = "per_user"
    PER_TEAM = "per_team"


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    challenge_type: Mapped[ChallengeType] = mapped_column(SQLEnum(ChallengeType), nullable=False)
    difficulty: Mapped[ChallengeDifficulty] = mapped_column(
        SQLEnum(ChallengeDifficulty), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tags: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    skills: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    lab_template_id: Mapped[int | None] = mapped_column(
        ForeignKey("lab_templates.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lab_template: Mapped[Optional["LabTemplate"]] = relationship()
    flags: Mapped[list["ChallengeFlag"]] = relationship(
        back_populates="challenge", cascade="all, delete-orphan"
    )
    hints: Mapped[list["ChallengeHint"]] = relationship(
        back_populates="challenge", cascade="all, delete-orphan", order_by="ChallengeHint.order_num"
    )
    files: Mapped[list["ChallengeFile"]] = relationship(
        back_populates="challenge", cascade="all, delete-orphan"
    )
    submissions: Mapped[list["ChallengeSubmission"]] = relationship(back_populates="challenge")
    deployments: Mapped[list["Deployment"]] = relationship(back_populates="challenge")


class ChallengeFlag(Base):
    __tablename__ = "challenge_flags"

    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    flag_type: Mapped[FlagType] = mapped_column(
        SQLEnum(FlagType), nullable=False, default=FlagType.STATIC
    )
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    regex_pattern: Mapped[str | None] = mapped_column(Text, nullable=True)
    hash_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    validation_script: Mapped[str | None] = mapped_column(Text, nullable=True)
    case_sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    challenge: Mapped["Challenge"] = relationship(back_populates="flags")


class ChallengeHint(Base):
    __tablename__ = "challenge_hints"
    __table_args__ = (
        UniqueConstraint("challenge_id", "order_num", name="uq_challenge_hints_challenge_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_num: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    challenge: Mapped["Challenge"] = relationship(back_populates="hints")
    unlocks: Mapped[list["HintUnlock"]] = relationship(
        back_populates="hint", cascade="all, delete-orphan"
    )


class ChallengeFile(Base):
    __tablename__ = "challenge_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)

    challenge: Mapped["Challenge"] = relationship(back_populates="files")


class ChallengeSubmission(Base):
    __tablename__ = "challenge_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("ctf_events.id"), nullable=True)
    submitted_value: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_first_blood: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    points_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    challenge: Mapped["Challenge"] = relationship(back_populates="submissions")
    user: Mapped["User"] = relationship(back_populates="challenge_submissions")
    team: Mapped[Optional["Team"]] = relationship()
    event: Mapped[Optional["CtfEvent"]] = relationship(back_populates="submissions")


class HintUnlock(Base):
    __tablename__ = "hint_unlocks"
    __table_args__ = (UniqueConstraint("hint_id", "user_id", name="uq_hint_unlocks_hint_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    hint_id: Mapped[int] = mapped_column(
        ForeignKey("challenge_hints.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    hint: Mapped["ChallengeHint"] = relationship(back_populates="unlocks")
