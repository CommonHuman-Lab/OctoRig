# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""add completed_at to assessment_invites

Revision ID: add_assessment_completed_at
Revises: drop_profile_twitter_handle
Create Date: 2026-06-19
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_assessment_completed_at"
down_revision: str | None = "drop_profile_twitter_handle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "assessment_invites",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("assessment_invites", "completed_at")
