# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Shared Deployment construction — allocates a subnet/IP and generates
per-deployment container/volume/network names and access_info, so the same
LabDefinition can back many concurrent Deployment rows without colliding.

Used by app/api/deployments.py, app/api/assessments.py, and
app/worker/tasks.py — each previously built the Deployment row inline with
slightly different (and collision-prone) logic.
"""
import copy
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.labs.registry import LabDefinition
from app.models.deployment import Deployment, DeploymentStatus, DeploymentVisibility
from app.models.lab_template import LabTemplate
from app.services.network_allocator import allocate_subnet


def prepare_deployment(
    db: Session,
    template: LabTemplate,
    lab_def: LabDefinition,
    *,
    started_by_id: int,
    team_id: int | None = None,
    challenge_id: int | None = None,
    instance_for_user_id: int | None = None,
    auto_destroy_at: datetime | None = None,
    visibility: DeploymentVisibility = DeploymentVisibility.PRIVATE,
) -> Deployment:
    """Builds and flushes a new Deployment with a unique subnet/IP and
    generated container/volume/network names. Caller is responsible for
    db.commit() (and any conflict checks before calling this)."""
    subnet = allocate_subnet(db)
    subnet_prefix = subnet.rsplit(".", 1)[0]
    app_ip = f"{subnet_prefix}.2"

    deployment = Deployment(
        lab_template_id=template.id,
        started_by_id=started_by_id,
        team_id=team_id,
        challenge_id=challenge_id,
        instance_for_user_id=instance_for_user_id,
        auto_destroy_at=auto_destroy_at,
        status=DeploymentStatus.STARTING,
        visibility=visibility,
        container_names=template.container_names,
        subnet=subnet,
        app_ip=app_ip,
    )
    db.add(deployment)
    db.flush()  # assigns deployment.id, needed to namespace names below

    suffix = str(deployment.id)
    deployment.network_name = f"octorig-{lab_def['slug']}-net-{suffix}"
    deployment.container_names = [f"{name}-{suffix}" for name in lab_def["container_names"]]
    deployment.volume_names = [f"{vol}-{suffix}" for vol in lab_def["volume_names"]]
    deployment.access_info = _scoped_access_info(lab_def, app_ip)
    db.flush()

    return deployment


def _scoped_access_info(lab_def: LabDefinition, app_ip: str) -> list[dict[str, Any]]:
    entries = copy.deepcopy(lab_def["access_info"])
    for entry in entries:
        entry["value"] = entry["value"].replace("{container_ip}", app_ip)
    return entries
