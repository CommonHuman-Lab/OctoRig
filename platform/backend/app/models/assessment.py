# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import secrets
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

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)

    # Company branding — overrides global SiteSettings for this assessment
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    candidate_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=48)

    # Lab config — list of lab slugs, e.g. ["humanbank", "subverse"]
    lab_slugs: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    # Display name overrides shown to candidates, e.g. {"subverse": "WebSec Universe"}
    lab_display_names: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])
    invites: Mapped[list["AssessmentInvite"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class AssessmentInvite(Base):
    __tablename__ = "assessment_invites"
    __table_args__ = (
        UniqueConstraint("assessment_id", "email", name="uq_invite_assessment_email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # secrets.token_urlsafe(32) on creation
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)

    # Null until candidate accepts the invite
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, unique=True
    )

    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # IDs of Deployment rows created for this candidate
    deployment_ids: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)

    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="invites")
    user: Mapped[Optional["User"]] = relationship(foreign_keys=[user_id])
    report: Mapped[Optional["AssessmentReport"]] = relationship(
        back_populates="invite", uselist=False, cascade="all, delete-orphan"
    )

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)


class AssessmentReport(Base):
    __tablename__ = "assessment_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    invite_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_invites.id"), nullable=False, unique=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    invite: Mapped["AssessmentInvite"] = relationship(back_populates="report")
