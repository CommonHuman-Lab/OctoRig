# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Unit tests for app.services.network_allocator — no Docker, no real network."""

from app.models.deployment import Deployment, DeploymentStatus
from app.services.network_allocator import allocate_subnet


def test_allocate_subnet_returns_a_cidr_in_the_pool(client, db_session):
    subnet = allocate_subnet(db_session)
    assert subnet.endswith("/24")
    assert subnet.startswith("10.90.")


def test_allocate_subnet_skips_subnets_already_in_use(client, db_session):
    first = allocate_subnet(db_session)

    db_session.add(
        Deployment(
            lab_template_id=1,
            started_by_id=1,
            status=DeploymentStatus.RUNNING,
            container_names=[],
            subnet=first,
        )
    )
    db_session.commit()

    second = allocate_subnet(db_session)
    assert second != first


def test_allocate_subnet_ignores_subnets_from_stopped_deployments(client, db_session):
    first = allocate_subnet(db_session)

    db_session.add(
        Deployment(
            lab_template_id=1,
            started_by_id=1,
            status=DeploymentStatus.STOPPED,
            container_names=[],
            subnet=first,
        )
    )
    db_session.commit()

    second = allocate_subnet(db_session)
    assert second == first
