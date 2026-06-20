# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""add is_owner flag — marks the single untouchable platform owner account

Revision ID: add_owner_flag
Revises: add_login_lockout
Create Date: 2026-06-19
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "add_owner_flag"
down_revision: Union[str, None] = "add_login_lockout"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_owner", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # Promote the earliest-created admin so existing deployments get a protected owner automatically
    op.execute(
        """
        UPDATE users SET is_owner = true
        WHERE id = (
            SELECT id FROM users
            WHERE platform_roles::jsonb ? 'admin'
            ORDER BY created_at ASC
            LIMIT 1
        )
        """
    )


def downgrade() -> None:
    op.drop_column("users", "is_owner")
