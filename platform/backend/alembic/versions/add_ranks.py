# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Add ranks table for the rank/level system.

Revision ID: add_ranks
Revises: hardening_indexes
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_ranks"
down_revision: str | None = "add_refresh_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ranks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("min_points", sa.Integer(), nullable=False, unique=True),
        sa.Column("icon", sa.String(64), nullable=True),
        sa.Column("color", sa.String(32), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_ranks_min_points", "ranks", ["min_points"])


def downgrade() -> None:
    op.drop_index("ix_ranks_min_points", table_name="ranks")
    op.drop_table("ranks")
