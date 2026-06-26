# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""drop is_admin/is_superuser flags in favor of platform_roles

Revision ID: drop_admin_superuser_flags
Revises: add_platform_roles
Create Date: 2026-06-18
"""

import sqlalchemy as sa

from alembic import op

revision: str = "drop_admin_superuser_flags"
down_revision: str | None = "add_platform_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Backfill: is_admin/is_superuser users get "admin" appended to platform_roles before the flags drop
    op.execute(
        """
        UPDATE users
        SET platform_roles = (
            SELECT to_jsonb(array_agg(DISTINCT elem))::json
            FROM (
                SELECT jsonb_array_elements_text(
                    COALESCE(platform_roles::jsonb, '[]'::jsonb) || '["admin"]'::jsonb
                ) AS elem
            ) sub
        )
        WHERE is_admin IS TRUE OR is_superuser IS TRUE
        """
    )
    op.drop_column("users", "is_superuser")
    op.drop_column("users", "is_admin")


def downgrade() -> None:
    op.add_column("users", sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute(
        """
        UPDATE users
        SET is_admin = TRUE, is_superuser = TRUE
        WHERE platform_roles::jsonb ? 'admin'
        """
    )
