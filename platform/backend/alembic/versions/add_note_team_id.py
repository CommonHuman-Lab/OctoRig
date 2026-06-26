# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Add team_id to notes — a user can belong to multiple teams, so team-visible notes
must target one specific team rather than "any of my teammates".

Revision ID: add_note_team_id
Revises: add_notes
"""
import sqlalchemy as sa

from alembic import op

revision: str = "add_note_team_id"
down_revision: str = "add_notes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notes", sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True))
    op.create_index("ix_notes_team_id", "notes", ["team_id"])


def downgrade() -> None:
    op.drop_index("ix_notes_team_id", table_name="notes")
    op.drop_column("notes", "team_id")
