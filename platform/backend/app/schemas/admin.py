# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any

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
    locked_until: datetime | None = None
    created_at: datetime
    last_login_at: datetime | None
    team_count: int
    deployment_count: int
    api_key_count: int


class AdminUserCreate(BaseModel):
    username: str
    email: str
    password: str
    platform_roles: list[str] = []


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    platform_roles: list[str] | None = None
    unlock: bool | None = None


class AdminResetPassword(BaseModel):
    new_password: str


class PlatformRoleResponse(ORMModel):
    id: int
    slug: str
    display_name: str
    description: str | None
    permissions: list[str]
    is_system: bool
    is_default: bool
    created_at: datetime


class PlatformRoleCreate(BaseModel):
    slug: str = Field(..., pattern=r"^[a-z0-9_-]+$", max_length=64)
    display_name: str = Field(..., max_length=128)
    description: str | None = None
    permissions: list[str] = []
    is_default: bool = False


class PlatformRoleUpdate(BaseModel):
    display_name: str | None = Field(None, max_length=128)
    description: str | None = None
    permissions: list[str] | None = None
    is_default: bool | None = None


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
    user_id: int | None
    username: str | None
    team_id: int | None
    team_name: str | None
    deployment_id: int | None
    action: str
    detail: dict[str, Any]
    ip_address: str | None
    created_at: datetime


class AdminApiKeyResponse(BaseModel):
    id: int
    user_id: int
    username: str
    name: str
    key_prefix: str
    expires_at: datetime | None
    last_used_at: datetime | None
    is_active: bool
    created_at: datetime


class SiteSettingsResponse(ORMModel):
    registration_open: bool
    maintenance_mode: bool
    maintenance_message: str | None
    max_flag_attempts: int | None
    dynamic_scoring_enabled: bool
    dynamic_decay_factor: float
    dynamic_min_floor_pct: int
    scoreboard_frozen_at: datetime | None
    first_blood_enabled: bool
    python_editor_enabled: bool
    hide_lab_ports: bool
    company_name: str | None
    company_logo_url: str | None
    default_theme: str | None
    default_locale: str | None
    updated_at: datetime


class SiteSettingsUpdate(BaseModel):
    registration_open: bool | None = None
    maintenance_mode: bool | None = None
    maintenance_message: str | None = None
    max_flag_attempts: int | None = Field(None, ge=1)
    dynamic_scoring_enabled: bool | None = None
    dynamic_decay_factor: float | None = Field(None, ge=0.0, le=1.0)
    dynamic_min_floor_pct: int | None = Field(None, ge=1, le=100)
    scoreboard_frozen_at: datetime | None = None
    first_blood_enabled: bool | None = None
    python_editor_enabled: bool | None = None
    hide_lab_ports: bool | None = None
    company_name: str | None = None
    company_logo_url: str | None = None
    default_theme: str | None = None
    default_locale: str | None = None


class PublicSettingsResponse(BaseModel):
    registration_open: bool
    maintenance_mode: bool
    maintenance_message: str | None
    first_blood_enabled: bool
    python_editor_enabled: bool
    company_name: str | None
    company_logo_url: str | None
    default_theme: str | None
    default_locale: str | None
