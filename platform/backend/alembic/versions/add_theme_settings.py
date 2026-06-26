# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""add theme settings

Revision ID: add_theme_settings
Revises: add_assessments
Create Date: 2026-06-17
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_theme_settings"
down_revision: str | None = "add_assessments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("site_settings", sa.Column("default_theme", sa.String(32), nullable=True))
    op.add_column("user_profiles", sa.Column("theme", sa.String(32), nullable=True))


def downgrade() -> None:
    op.drop_column("site_settings", "default_theme")
    op.drop_column("user_profiles", "theme")
