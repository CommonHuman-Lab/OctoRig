# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Production hardening: missing indexes and deployment uniqueness constraint.

Revision ID: hardening_indexes
Revises: add_challenge_lab_tmpl
"""

from alembic import op

revision: str = "hardening_indexes"
down_revision: str | None = "add_challenge_lab_tmpl"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Missing FK indexes on deployments ---
    # started_by_id has no index; querying "all deployments by user" is a full table scan.
    op.create_index("ix_deployments_started_by_id", "deployments", ["started_by_id"])

    # instance_for_user_id has no index; used in per-user challenge instance lookups.
    op.create_index(
        "ix_deployments_instance_for_user_id", "deployments", ["instance_for_user_id"]
    )

    # Composite index for the auto-destroy sweep (status + auto_destroy_at every 60s).
    op.create_index(
        "ix_deployments_auto_destroy",
        "deployments",
        ["auto_destroy_at", "status"],
    )

    # Partial unique index closes the TOCTOU window between the app-level conflict check and INSERT
    op.execute(
        """
        CREATE UNIQUE INDEX uq_one_active_deployment_per_template
            ON deployments (lab_template_id)
            WHERE status IN ('starting', 'running')
        """
    )

    # Same uniqueness for per-user challenge instances: one active instance per
    # (challenge_id, instance_for_user_id) pair.
    op.execute(
        """
        CREATE UNIQUE INDEX uq_one_active_challenge_instance_per_user
            ON deployments (challenge_id, instance_for_user_id)
            WHERE status IN ('starting', 'running')
              AND challenge_id IS NOT NULL
              AND instance_for_user_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_one_active_challenge_instance_per_user")
    op.execute("DROP INDEX IF EXISTS uq_one_active_deployment_per_template")
    op.drop_index("ix_deployments_auto_destroy", table_name="deployments")
    op.drop_index("ix_deployments_instance_for_user_id", table_name="deployments")
    op.drop_index("ix_deployments_started_by_id", table_name="deployments")
