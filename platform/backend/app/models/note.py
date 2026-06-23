# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from app.core.db_types import EnumCol as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.challenge import Challenge
    from app.models.lab_template import LabTemplate
    from app.models.team import Team
    from app.models.user import User


class NoteVisibility(str, enum.Enum):
    PRIVATE = "private"
    TEAM = "team"


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    lab_template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("lab_templates.id"), nullable=True, index=True
    )
    challenge_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("challenges.id"), nullable=True, index=True
    )
    visibility: Mapped[NoteVisibility] = mapped_column(
        SQLEnum(NoteVisibility), nullable=False, default=NoteVisibility.PRIVATE
    )
    team_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("teams.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="notes")
    lab_template: Mapped[Optional["LabTemplate"]] = relationship()
    challenge: Mapped[Optional["Challenge"]] = relationship()
    team: Mapped[Optional["Team"]] = relationship()
