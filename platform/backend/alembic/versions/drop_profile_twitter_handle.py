# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""drop twitter_handle from user_profiles

Revision ID: drop_profile_twitter_handle
Revises: drop_lab_template_static_network
Create Date: 2026-06-19
"""

import sqlalchemy as sa

from alembic import op

revision: str = "drop_profile_twitter_handle"
down_revision: str | None = "drop_lab_template_static_network"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("user_profiles", "twitter_handle")


def downgrade() -> None:
    op.add_column("user_profiles", sa.Column("twitter_handle", sa.String(64), nullable=True))
