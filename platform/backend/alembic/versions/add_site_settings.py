# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Add site_settings singleton table for platform-wide configuration.

Revision ID: add_site_settings
Revises: add_ranks
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_site_settings"
down_revision: str | None = "add_ranks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("registration_open", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("maintenance_mode", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("maintenance_message", sa.Text(), nullable=True),
        sa.Column("max_flag_attempts", sa.Integer(), nullable=True),
        sa.Column("dynamic_scoring_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("dynamic_decay_factor", sa.Float(), nullable=False, server_default="0.9"),
        sa.Column("dynamic_min_floor_pct", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("scoreboard_frozen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_blood_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.execute("INSERT INTO site_settings (id) VALUES (1)")


def downgrade() -> None:
    op.drop_table("site_settings")
