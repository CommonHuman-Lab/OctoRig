# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from app.core.db_types import EnumCol as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class PrivacyLevel(str, enum.Enum):
    PUBLIC = "public"
    TEAM_ONLY = "team_only"
    PRIVATE = "private"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    github_handle: Mapped[str | None] = mapped_column(String(64), nullable=True)
    privacy_level: Mapped[PrivacyLevel] = mapped_column(
        SQLEnum(PrivacyLevel), nullable=False, default=PrivacyLevel.PUBLIC
    )
    show_activity: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    theme: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    locale: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="profile")
