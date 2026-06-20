# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Drop LabTemplate.network_name/subnet/app_ip — vestigial since networking moved to per-deployment allocation.

Revision ID: drop_lab_template_static_network
Revises: add_hide_lab_ports
Create Date: 2026-06-19
"""
from typing import Union

from alembic import op

revision: str = "drop_lab_template_static_network"
down_revision: Union[str, None] = "add_hide_lab_ports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("lab_templates", "network_name")
    op.drop_column("lab_templates", "subnet")
    op.drop_column("lab_templates", "app_ip")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column("lab_templates", sa.Column("app_ip", sa.String(length=32), nullable=False, server_default=""))
    op.add_column("lab_templates", sa.Column("subnet", sa.String(length=32), nullable=False, server_default=""))
    op.add_column("lab_templates", sa.Column("network_name", sa.String(length=128), nullable=False, server_default=""))
