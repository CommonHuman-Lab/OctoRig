# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""add hide_lab_ports setting

Revision ID: add_hide_lab_ports
Revises: add_deployment_network_isolation
Create Date: 2026-06-19
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_hide_lab_ports"
down_revision: str | None = "add_deployment_network_isolation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_settings",
        sa.Column("hide_lab_ports", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column("site_settings", "hide_lab_ports")
