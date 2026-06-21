# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Optional

from app.schemas.base import ORMModel


class DeploymentSummary(ORMModel):
    id: int
    status: str
    started_at: Optional[datetime]
    subnet: Optional[str] = None
    app_ip: Optional[str] = None
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
    current_deployment: Optional[DeploymentSummary] = None
