# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    JSON,
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
    from app.models.user import User


class AchievementRuleType(str, enum.Enum):
    SOLVE_COUNT = "solve_count"
    FIRST_BLOOD = "first_blood"
    STREAK_DAYS = "streak_days"
    CATEGORY_COMPLETE = "category_complete"
    POINTS_THRESHOLD = "points_threshold"
    MANUAL = "manual"


class BadgeDefinition(Base):
    __tablename__ = "badge_definitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(64), nullable=False, default="shield")
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    points_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    rules: Mapped[list["AchievementRule"]] = relationship(
        back_populates="badge", cascade="all, delete-orphan"
    )
    user_badges: Mapped[list["UserBadge"]] = relationship(back_populates="badge")


class AchievementRule(Base):
    __tablename__ = "achievement_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badge_definitions.id"), nullable=False, index=True)
    rule_type: Mapped[AchievementRuleType] = mapped_column(SQLEnum(AchievementRuleType), nullable=False)
    rule_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    badge: Mapped["BadgeDefinition"] = relationship(back_populates="rules")


class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (
        UniqueConstraint("user_id", "badge_id", name="uq_user_badges"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badge_definitions.id"), nullable=False)
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    awarded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="user_badges")
    badge: Mapped["BadgeDefinition"] = relationship(back_populates="user_badges")
    awarded_by: Mapped[Optional["User"]] = relationship(foreign_keys=[awarded_by_id])
