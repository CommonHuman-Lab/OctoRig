# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Per-deployment network isolation — dynamic subnet/IP/container/volume naming.

Replaces the global "one active deployment per lab template" constraint with
per-user / per-team scoping, so different users/teams can run the same lab
concurrently. Networking details that used to live statically on LabTemplate
now get allocated fresh per Deployment.

Revision ID: add_deployment_network_isolation
Revises: add_owner_flag
Create Date: 2026-06-19
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_deployment_network_isolation"
down_revision: str | None = "add_owner_flag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("deployments", sa.Column("subnet", sa.String(length=32), nullable=True))
    op.add_column("deployments", sa.Column("app_ip", sa.String(length=32), nullable=True))
    op.add_column("deployments", sa.Column("network_name", sa.String(length=128), nullable=True))
    op.add_column(
        "deployments",
        sa.Column("volume_names", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "deployments",
        sa.Column("access_info", sa.JSON(), nullable=False, server_default="[]"),
    )

    # Single-row mutex table — SELECT ... FOR UPDATE on its one row serializes
    # subnet allocation across concurrent requests/workers.
    op.create_table(
        "network_allocation_locks",
        sa.Column("id", sa.Integer(), primary_key=True),
    )
    op.execute("INSERT INTO network_allocation_locks (id) VALUES (1)")

    # Active deployments predate per-deployment naming and won't match it, so force-stop them
    op.execute(
        """
        UPDATE deployments SET status = 'stopped', stopped_at = now()
        WHERE status IN ('starting', 'running')
        """
    )

    op.execute("DROP INDEX IF EXISTS uq_one_active_deployment_per_template")

    op.execute(
        """
        CREATE UNIQUE INDEX uq_one_active_deployment_per_template_per_user
            ON deployments (lab_template_id, started_by_id)
            WHERE status IN ('starting', 'running') AND team_id IS NULL
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_one_active_deployment_per_template_per_team
            ON deployments (lab_template_id, team_id)
            WHERE status IN ('starting', 'running') AND team_id IS NOT NULL
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_active_deployment_subnet
            ON deployments (subnet)
            WHERE status IN ('starting', 'running') AND subnet IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_active_deployment_subnet")
    op.execute("DROP INDEX IF EXISTS uq_one_active_deployment_per_template_per_team")
    op.execute("DROP INDEX IF EXISTS uq_one_active_deployment_per_template_per_user")
    op.execute(
        """
        CREATE UNIQUE INDEX uq_one_active_deployment_per_template
            ON deployments (lab_template_id)
            WHERE status IN ('starting', 'running')
        """
    )
    op.drop_table("network_allocation_locks")
    op.drop_column("deployments", "access_info")
    op.drop_column("deployments", "volume_names")
    op.drop_column("deployments", "network_name")
    op.drop_column("deployments", "app_ip")
    op.drop_column("deployments", "subnet")
