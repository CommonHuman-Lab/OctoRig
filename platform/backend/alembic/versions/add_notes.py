# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Add notes table for personal/team-shared user notes, optionally linked to a lab or challenge.

Revision ID: add_notes
Revises: add_assessment_completed_at
"""

import sqlalchemy as sa

from alembic import op

revision: str = "add_notes"
down_revision: str = "add_assessment_completed_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    notevisibility = sa.Enum("private", "team", name="notevisibility")

    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "lab_template_id", sa.Integer(), sa.ForeignKey("lab_templates.id"), nullable=True
        ),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id"), nullable=True),
        sa.Column("visibility", notevisibility, nullable=False, server_default="private"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_notes_owner_id", "notes", ["owner_id"])
    op.create_index("ix_notes_lab_template_id", "notes", ["lab_template_id"])
    op.create_index("ix_notes_challenge_id", "notes", ["challenge_id"])


def downgrade() -> None:
    op.drop_table("notes")
    op.execute("DROP TYPE IF EXISTS notevisibility")
