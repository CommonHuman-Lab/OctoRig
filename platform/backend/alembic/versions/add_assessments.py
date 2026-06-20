# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Add Assessment Mode: assessments, assessment_invites, assessment_reports tables.
Also adds is_candidate to users and company branding columns to site_settings.

Revision ID: add_assessments
Revises: add_python_editor_toggle
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "add_assessments"
down_revision: Union[str, None] = "add_python_editor_toggle"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_candidate", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.add_column("site_settings", sa.Column("company_name", sa.String(255), nullable=True))
    op.add_column("site_settings", sa.Column("company_logo_url", sa.Text(), nullable=True))

    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(128), nullable=False, unique=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("company_logo_url", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("candidate_instructions", sa.Text(), nullable=True),
        sa.Column("duration_hours", sa.Integer(), nullable=False, server_default="48"),
        sa.Column("lab_slugs", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("lab_display_names", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_assessments_slug", "assessments", ["slug"])

    op.create_table(
        "assessment_invites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("candidate_name", sa.String(255), nullable=True),
        sa.Column("token", sa.String(128), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, unique=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deployment_ids", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default="false"),
        sa.UniqueConstraint("assessment_id", "email", name="uq_invite_assessment_email"),
    )
    op.create_index("ix_assessment_invites_assessment_id", "assessment_invites", ["assessment_id"])
    op.create_index("ix_assessment_invites_token", "assessment_invites", ["token"])

    op.create_table(
        "assessment_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "invite_id",
            sa.Integer(),
            sa.ForeignKey("assessment_invites.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

def downgrade() -> None:
    op.drop_table("assessment_reports")
    op.drop_index("ix_assessment_invites_token", "assessment_invites")
    op.drop_index("ix_assessment_invites_assessment_id", "assessment_invites")
    op.drop_table("assessment_invites")
    op.drop_index("ix_assessments_slug", "assessments")
    op.drop_table("assessments")
    op.drop_column("site_settings", "company_logo_url")
    op.drop_column("site_settings", "company_name")
    op.drop_column("users", "is_candidate")
