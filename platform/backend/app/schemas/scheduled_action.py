# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

from app.models.scheduled_action import ScheduledActionStatus, ScheduledActionType
from app.schemas.base import ORMModel


class ScheduledActionCreate(BaseModel):
    action: ScheduledActionType
    scheduled_at: datetime
    team_id: Optional[int] = None
    lab_template_id: Optional[int] = None
    deployment_id: Optional[int] = None

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
    team_id: Optional[int]
    lab_template_id: Optional[int]
    deployment_id: Optional[int]
    action: ScheduledActionType
    scheduled_at: datetime
    executed_at: Optional[datetime]
    status: ScheduledActionStatus
    error_message: Optional[str]
    created_at: datetime
