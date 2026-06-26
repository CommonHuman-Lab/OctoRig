# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_types import EnumCol as SQLEnum
from app.database import Base

if TYPE_CHECKING:
    from app.models.deployment import Deployment
    from app.models.lab_template import LabTemplate
    from app.models.team import Team
    from app.models.user import User


class ScheduledActionType(str, enum.Enum):
    DEPLOY = "deploy"
    DESTROY = "destroy"


class ScheduledActionStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduledAction(Base):
    __tablename__ = "scheduled_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    lab_template_id: Mapped[int | None] = mapped_column(ForeignKey("lab_templates.id"), nullable=True)
    deployment_id: Mapped[int | None] = mapped_column(ForeignKey("deployments.id"), nullable=True)
    action: Mapped[ScheduledActionType] = mapped_column(SQLEnum(ScheduledActionType), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ScheduledActionStatus] = mapped_column(
        SQLEnum(ScheduledActionStatus), nullable=False, default=ScheduledActionStatus.PENDING
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="scheduled_actions")
    team: Mapped[Optional["Team"]] = relationship(back_populates="scheduled_actions")
    lab_template: Mapped[Optional["LabTemplate"]] = relationship(back_populates="scheduled_actions")
    deployment: Mapped[Optional["Deployment"]] = relationship(back_populates="scheduled_actions")
