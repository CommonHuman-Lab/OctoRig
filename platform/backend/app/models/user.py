# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.api_key import ApiKey
    from app.models.assessment import AssessmentInvite
    from app.models.audit_log import AuditLog
    from app.models.badge import UserBadge
    from app.models.challenge import ChallengeSubmission
    from app.models.deployment import Deployment
    from app.models.note import Note
    from app.models.notification import Notification, NotificationPreference
    from app.models.profile import UserProfile
    from app.models.refresh_token import RefreshToken
    from app.models.scheduled_action import ScheduledAction
    from app.models.team import Team, TeamMember


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_candidate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    platform_roles: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    deployments: Mapped[list["Deployment"]] = relationship(
        foreign_keys="Deployment.started_by_id", back_populates="user"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")
    created_teams: Mapped[list["Team"]] = relationship(
        foreign_keys="Team.created_by_id", back_populates="created_by"
    )
    team_memberships: Mapped[list["TeamMember"]] = relationship(
        foreign_keys="TeamMember.user_id", back_populates="user"
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="user")
    scheduled_actions: Mapped[list["ScheduledAction"]] = relationship(back_populates="user")
    challenge_submissions: Mapped[list["ChallengeSubmission"]] = relationship(back_populates="user")
    user_badges: Mapped[list["UserBadge"]] = relationship(
        foreign_keys="UserBadge.user_id", back_populates="user"
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    notification_preferences: Mapped[Optional["NotificationPreference"]] = relationship(
        back_populates="user"
    )
    profile: Mapped[Optional["UserProfile"]] = relationship(back_populates="user")
    notes: Mapped[list["Note"]] = relationship(back_populates="owner")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    assessment_invite: Mapped[Optional["AssessmentInvite"]] = relationship(
        foreign_keys="AssessmentInvite.user_id", back_populates="user", uselist=False
    )
