# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Add required_lab_slugs JSON column to challenges for cross-lab awareness.

Revision ID: add_challenge_required_lab_slugs
Revises: hardening_indexes
"""

import sqlalchemy as sa
from alembic import op

revision: str = "add_challenge_required_lab_slugs"
down_revision: str | None = "add_locale_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "challenges",
        sa.Column("required_lab_slugs", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("challenges", "required_lab_slugs")
