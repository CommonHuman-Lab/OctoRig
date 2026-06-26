# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime

from pydantic import BaseModel

from app.schemas.base import ORMModel


class ApiKeyCreate(BaseModel):
    name: str
    expires_at: datetime | None = None


class ApiKeyResponse(ORMModel):
    id: int
    name: str
    key_prefix: str
    expires_at: datetime | None
    last_used_at: datetime | None
    is_active: bool
    created_at: datetime


class ApiKeyCreated(ApiKeyResponse):
    """Returned only at creation time — includes the raw key shown once."""

    raw_key: str
