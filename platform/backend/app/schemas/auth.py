# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(ORMModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_candidate: bool
    platform_roles: list[str] = []
    permissions: list[str] = []
    created_at: datetime
    last_login_at: Optional[datetime]
