# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_types import EnumCol as SQLEnum
from app.database import Base

if TYPE_CHECKING:
    from app.models.ctf_event import CtfEvent
    from app.models.team import Team
    from app.models.user import User


class ScoreTransactionSource(str, enum.Enum):
    CHALLENGE_SOLVE = "challenge_solve"
    BADGE_AWARD = "badge_award"
    HINT_COST = "hint_cost"
    MANUAL_ADJUST = "manual_adjust"
    PENALTY = "penalty"


class ScoreTransaction(Base):
    __tablename__ = "score_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("ctf_events.id"), nullable=True)
    source_type: Mapped[ScoreTransactionSource] = mapped_column(
        SQLEnum(ScoreTransactionSource), nullable=False
    )
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship()
    team: Mapped[Optional["Team"]] = relationship()
    event: Mapped[Optional["CtfEvent"]] = relationship(back_populates="score_transactions")
