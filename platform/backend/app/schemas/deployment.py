# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any

from pydantic import BaseModel, model_validator

from app.models.deployment import DeploymentStatus, DeploymentVisibility
from app.schemas.base import ORMModel


class DeploymentCreate(BaseModel):
    lab_template_id: int | None = None
    challenge_id: int | None = None
    team_id: int | None = None
    visibility: DeploymentVisibility = DeploymentVisibility.PRIVATE
    ttl_hours: int = 2  # 1–8 hours

    @model_validator(mode="after")
    def require_template_or_challenge(self) -> "DeploymentCreate":
        if self.lab_template_id is None and self.challenge_id is None:
            raise ValueError("At least one of lab_template_id or challenge_id must be provided")
        return self


class DeploymentResponse(ORMModel):
    id: int
    lab_template_id: int
    started_by_id: int
    team_id: int | None
    challenge_id: int | None = None
    instance_for_user_id: int | None = None
    auto_destroy_at: datetime | None = None
    dynamic_flag: str | None = None
    status: DeploymentStatus
    visibility: DeploymentVisibility
    container_names: list[str]
    container_ids: dict[str, Any]
    subnet: str | None = None
    app_ip: str | None = None
    network_name: str | None = None
    access_info: list[dict[str, str]] = []
    error_message: str | None
    started_at: datetime | None
    stopped_at: datetime | None
    created_at: datetime


class DeploymentWithTemplate(DeploymentResponse):
    lab_name: str
    lab_slug: str
    lab_category: str
    started_by_username: str
    team_name: str | None = None
