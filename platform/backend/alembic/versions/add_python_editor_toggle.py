# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Add python_editor_enabled toggle to site_settings.

Revision ID: add_python_editor_toggle
Revises: add_site_settings
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_python_editor_toggle"
down_revision: str | None = "add_site_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_settings",
        sa.Column("python_editor_enabled", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    op.drop_column("site_settings", "python_editor_enabled")
