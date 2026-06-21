# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any, Optional

from app.schemas.base import ORMModel


class AuditLogResponse(ORMModel):
    id: int
    user_id: Optional[int]
    deployment_id: Optional[int]
    action: str
    detail: dict[str, Any]
    ip_address: Optional[str]
    created_at: datetime
