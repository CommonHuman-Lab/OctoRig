# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.base import ORMModel


class SystemStats(BaseModel):
    user_count: int
    team_count: int
    active_deployments: int
    total_deployments: int
    api_key_count: int
    pending_scheduled_actions: int


class AdminUserResponse(ORMModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_owner: bool = False
    platform_roles: list[str] = []
    locked_until: Optional[datetime] = None
    created_at: datetime
    last_login_at: Optional[datetime]
    team_count: int
    deployment_count: int
    api_key_count: int


class AdminUserCreate(BaseModel):
    username: str
    email: str
    password: str
    platform_roles: list[str] = []


class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    platform_roles: Optional[list[str]] = None
    unlock: Optional[bool] = None


class AdminResetPassword(BaseModel):
    new_password: str


class PlatformRoleResponse(ORMModel):
    id: int
    slug: str
    display_name: str
    description: Optional[str]
    permissions: list[str]
    is_system: bool
    is_default: bool
    created_at: datetime


class PlatformRoleCreate(BaseModel):
    slug: str = Field(..., pattern=r"^[a-z0-9_-]+$", max_length=64)
    display_name: str = Field(..., max_length=128)
    description: Optional[str] = None
    permissions: list[str] = []
    is_default: bool = False


class PlatformRoleUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None
    permissions: Optional[list[str]] = None
    is_default: Optional[bool] = None


class AdminTeamResponse(ORMModel):
    id: int
    name: str
    slug: str
    is_personal: bool
    created_by_id: int
    created_by_username: str
    member_count: int
    deployment_count: int
    created_at: datetime


class AdminAuditLogResponse(ORMModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    team_id: Optional[int]
    team_name: Optional[str]
    deployment_id: Optional[int]
    action: str
    detail: dict[str, Any]
    ip_address: Optional[str]
    created_at: datetime


class AdminApiKeyResponse(BaseModel):
    id: int
    user_id: int
    username: str
    name: str
    key_prefix: str
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    created_at: datetime


class SiteSettingsResponse(ORMModel):
    registration_open: bool
    maintenance_mode: bool
    maintenance_message: Optional[str]
    max_flag_attempts: Optional[int]
    dynamic_scoring_enabled: bool
    dynamic_decay_factor: float
    dynamic_min_floor_pct: int
    scoreboard_frozen_at: Optional[datetime]
    first_blood_enabled: bool
    python_editor_enabled: bool
    hide_lab_ports: bool
    company_name: Optional[str]
    company_logo_url: Optional[str]
    default_theme: Optional[str]
    default_locale: Optional[str]
    updated_at: datetime


class SiteSettingsUpdate(BaseModel):
    registration_open: Optional[bool] = None
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    max_flag_attempts: Optional[int] = Field(None, ge=1)
    dynamic_scoring_enabled: Optional[bool] = None
    dynamic_decay_factor: Optional[float] = Field(None, ge=0.0, le=1.0)
    dynamic_min_floor_pct: Optional[int] = Field(None, ge=1, le=100)
    scoreboard_frozen_at: Optional[datetime] = None
    first_blood_enabled: Optional[bool] = None
    python_editor_enabled: Optional[bool] = None
    hide_lab_ports: Optional[bool] = None
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None
    default_theme: Optional[str] = None
    default_locale: Optional[str] = None


class PublicSettingsResponse(BaseModel):
    registration_open: bool
    maintenance_mode: bool
    maintenance_message: Optional[str]
    first_blood_enabled: bool
    python_editor_enabled: bool
    company_name: Optional[str]
    company_logo_url: Optional[str]
    default_theme: Optional[str]
    default_locale: Optional[str]
