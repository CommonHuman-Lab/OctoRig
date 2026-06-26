# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""add platform roles

Revision ID: add_platform_roles
Revises: add_theme_settings
Create Date: 2026-06-18
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_platform_roles"
down_revision: str | None = "add_theme_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "platform_roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("permissions", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_platform_roles_slug", "platform_roles", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_platform_roles_slug", table_name="platform_roles")
    op.drop_table("platform_roles")
