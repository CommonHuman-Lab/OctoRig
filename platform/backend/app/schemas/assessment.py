# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.deployment import DeploymentStatus
from app.schemas.base import ORMModel

# --- Assessment ---


class AssessmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    company_name: str | None = Field(None, max_length=255)
    company_logo_url: str | None = None
    description: str | None = None
    candidate_instructions: str | None = None
    duration_hours: int = Field(48, ge=1, le=720)
    lab_slugs: list[str] = Field(..., min_length=1)
    lab_display_names: dict[str, str] = Field(default_factory=dict)


class AssessmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    company_name: str | None = Field(None, max_length=255)
    company_logo_url: str | None = None
    description: str | None = None
    candidate_instructions: str | None = None
    duration_hours: int | None = Field(None, ge=1, le=720)
    lab_slugs: list[str] | None = None
    lab_display_names: dict[str, str] | None = None
    is_active: bool | None = None


class AssessmentResponse(ORMModel):
    id: int
    name: str
    slug: str
    company_name: str | None
    company_logo_url: str | None
    description: str | None
    candidate_instructions: str | None
    duration_hours: int
    lab_slugs: list[Any]
    lab_display_names: dict[str, Any]
    is_active: bool
    created_by_id: int
    created_at: datetime
    invite_count: int = 0
    active_invite_count: int = 0


# --- AssessmentInvite ---

InviteStatus = Literal["pending", "accepted", "active", "completed", "expired", "revoked"]


class AssessmentInviteCreate(BaseModel):
    email: str = Field(..., max_length=255)
    candidate_name: str | None = Field(None, max_length=255)


class AssessmentInviteResponse(ORMModel):
    id: int
    assessment_id: int
    email: str
    candidate_name: str | None
    token: str
    user_id: int | None
    accepted_at: datetime | None
    started_at: datetime | None
    expires_at: datetime | None
    completed_at: datetime | None
    deployment_ids: list[Any]
    is_revoked: bool
    status: InviteStatus


class FlagSolve(BaseModel):
    challenge_slug: str
    challenge_title: str
    points: int
    solved_at: datetime


class AssessmentInviteWithProgress(AssessmentInviteResponse):
    flags_solved: list[FlagSolve] = []
    score: int = 0
    report_submitted: bool = False
    report_content: str | None = None


# --- Candidate-facing ---


class InviteLandingResponse(BaseModel):
    """Public info shown on the invite landing page — no internal slugs exposed."""

    assessment_name: str
    company_name: str | None
    company_logo_url: str | None
    candidate_instructions: str | None
    lab_count: int
    duration_hours: int
    candidate_name: str | None
    status: InviteStatus


class CandidateLabInfo(BaseModel):
    display_name: str
    slug: str
    deployment_id: int | None
    status: DeploymentStatus | None
    access_info: list[dict[str, Any]]


class CandidateAssessmentStatus(BaseModel):
    assessment_name: str
    company_name: str | None
    company_logo_url: str | None
    candidate_instructions: str | None
    started_at: datetime | None
    expires_at: datetime | None
    completed_at: datetime | None
    time_remaining_seconds: int | None
    labs: list[CandidateLabInfo]
    report_submitted: bool
    report_content: str | None


# --- Report ---


class ReportSubmit(BaseModel):
    content: str = Field(..., min_length=1)


class ReportResponse(ORMModel):
    invite_id: int
    content: str
    submitted_at: datetime


# --- Invite accept (registration flow) ---


class InviteAcceptRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=8)
