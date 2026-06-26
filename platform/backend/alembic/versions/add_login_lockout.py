# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""add account lockout fields for login brute-force protection

Revision ID: add_login_lockout
Revises: drop_admin_superuser_flags
Create Date: 2026-06-18
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_login_lockout"
down_revision: str | None = "drop_admin_superuser_flags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")
