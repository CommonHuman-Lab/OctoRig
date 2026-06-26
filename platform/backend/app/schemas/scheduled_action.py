# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime

from pydantic import BaseModel, model_validator

from app.models.scheduled_action import ScheduledActionStatus, ScheduledActionType
from app.schemas.base import ORMModel


class ScheduledActionCreate(BaseModel):
    action: ScheduledActionType
    scheduled_at: datetime
    team_id: int | None = None
    lab_template_id: int | None = None
    deployment_id: int | None = None

    @model_validator(mode="after")
    def validate_target(self) -> "ScheduledActionCreate":
        if self.action == ScheduledActionType.DEPLOY and self.lab_template_id is None:
            raise ValueError("lab_template_id is required for deploy actions")
        if self.action == ScheduledActionType.DESTROY and self.deployment_id is None:
            raise ValueError("deployment_id is required for destroy actions")
        return self


class ScheduledActionResponse(ORMModel):
    id: int
    user_id: int
    team_id: int | None
    lab_template_id: int | None
    deployment_id: int | None
    action: ScheduledActionType
    scheduled_at: datetime
    executed_at: datetime | None
    status: ScheduledActionStatus
    error_message: str | None
    created_at: datetime
