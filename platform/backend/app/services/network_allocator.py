# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Per-deployment subnet allocation out of a fixed /16 pool.

allocate_subnet() must be called inside the same DB transaction that will
insert/commit the Deployment row, so the SELECT ... FOR UPDATE lock held
here actually serializes concurrent allocations. The partial unique index
on deployments.subnet (see alembic/versions/add_deployment_network_isolation.py)
is the second line of defence in Postgres.
"""

import ipaddress

from sqlalchemy.orm import Session

from app.config import settings
from app.models.deployment import Deployment, DeploymentStatus, NetworkAllocationLock


def allocate_subnet(db: Session) -> str:
    lock_row = db.query(NetworkAllocationLock).with_for_update().first()
    if lock_row is None:
        # Self-heals if the migration's seed row is missing, e.g. test DBs using create_all()
        db.add(NetworkAllocationLock(id=1))
        db.flush()

    used = {
        s
        for (s,) in db.query(Deployment.subnet).filter(
            Deployment.status.in_([DeploymentStatus.STARTING, DeploymentStatus.RUNNING]),
            Deployment.subnet.isnot(None),
        )
    }

    pool = ipaddress.ip_network(settings.network_pool_cidr)
    for candidate in pool.subnets(new_prefix=24):
        cidr = str(candidate)
        if cidr not in used:
            return cidr

    raise RuntimeError(f"No free subnets left in pool {settings.network_pool_cidr}")
