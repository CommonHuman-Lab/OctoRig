# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any

from app.schemas.base import ORMModel


class AuditLogResponse(ORMModel):
    id: int
    user_id: int | None
    deployment_id: int | None
    action: str
    detail: dict[str, Any]
    ip_address: str | None
    created_at: datetime
