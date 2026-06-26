# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime

from app.schemas.base import ORMModel


class DeploymentSummary(ORMModel):
    id: int
    status: str
    started_at: datetime | None
    subnet: str | None = None
    app_ip: str | None = None
    container_names: list[str] = []
    access_info: list[dict[str, str]] = []


class LabTemplateResponse(ORMModel):
    id: int
    slug: str
    name: str
    description: str
    category: str
    container_names: list[str]
    images: dict[str, str]
    build_contexts: dict[str, str]
    start_order: list[str]
    exposed_ports: dict[str, int]
    access_info: list[dict[str, str]]
    volume_names: list[str]
    requires_privileged: bool
    is_active: bool
    current_deployment: DeploymentSummary | None = None
