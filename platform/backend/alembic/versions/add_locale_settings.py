# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""add locale settings

Revision ID: add_locale_settings
Revises: add_note_team_id
Create Date: 2026-06-23
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "add_locale_settings"
down_revision: Union[str, None] = "add_note_team_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("site_settings", sa.Column("default_locale", sa.String(8), nullable=True))
    op.add_column("user_profiles", sa.Column("locale", sa.String(8), nullable=True))


def downgrade() -> None:
    op.drop_column("site_settings", "default_locale")
    op.drop_column("user_profiles", "locale")
