# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Complete database schema initialization with all tables, enums, indexes, and constraints needed for the application.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "db_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    deploymentstatus = sa.Enum(
        "starting", "running", "stopping", "stopped", "error",
        name="deploymentstatus",
    )
    deploymentvisibility = sa.Enum(
        "private", "team", "public",
        name="deploymentvisibility",
    )
    teamrole = sa.Enum(
        "owner", "manager", "member", "viewer",
        name="teamrole",
    )
    scheduledactiontype = sa.Enum(
        "deploy", "destroy",
        name="scheduledactiontype",
    )
    scheduledactionstatus = sa.Enum(
        "pending", "executing", "completed", "failed", "cancelled",
        name="scheduledactionstatus",
    )

    challengetype = sa.Enum(
        "flag", "mcq", "short_answer", "file_upload",
        "dynamic_flag", "api", "web", "container",
        name="challengetype",
    )
    challengedifficulty = sa.Enum(
        "easy", "medium", "hard", "insane",
        name="challengedifficulty",
    )
    flagtype = sa.Enum(
        "static", "dynamic", "per_user", "per_team",
        name="flagtype",
    )
    scoretransactionsource = sa.Enum(
        "challenge_solve", "badge_award", "hint_cost", "manual_adjust", "penalty",
        name="scoretransactionsource",
    )
    eventstatus = sa.Enum(
        "draft", "published", "running", "ended", "archived",
        name="eventstatus",
    )
    eventvisibility = sa.Enum(
        "public", "private", "unlisted",
        name="eventvisibility",
    )
    eventscoringmode = sa.Enum(
        "static", "dynamic",
        name="eventscoringmode",
    )
    achievementruletype = sa.Enum(
        "solve_count", "first_blood", "streak_days",
        "category_complete", "points_threshold", "manual",
        name="achievementruletype",
    )
    privacylevel = sa.Enum(
        "public", "team_only", "private",
        name="privacylevel",
    )
    contenttype = sa.Enum(
        "challenge", "lab",
        name="contenttype",
    )
    contentstatus = sa.Enum(
        "draft", "pending_review", "in_review", "approved", "published", "rejected",
        name="contentstatus",
    )
    reviewverdict = sa.Enum(
        "approved", "rejected", "needs_changes",
        name="reviewverdict",
    )
    packagetype = sa.Enum(
        "lab_pack", "challenge_pack", "exercise",
        name="packagetype",
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("platform_roles", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "lab_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("container_names", sa.JSON(), nullable=False),
        sa.Column("images", sa.JSON(), nullable=False),
        sa.Column("build_contexts", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("start_order", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("network_name", sa.String(128), nullable=False),
        sa.Column("subnet", sa.String(32), nullable=False),
        sa.Column("app_ip", sa.String(32), nullable=False),
        sa.Column("exposed_ports", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("access_info", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("volume_names", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("env_vars", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("requires_privileged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_lab_templates_slug", "lab_templates", ["slug"])

    op.create_table(
        "challenges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("challenge_type", challengetype, nullable=False),
        sa.Column("difficulty", challengedifficulty, nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("content", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_challenges_slug", "challenges", ["slug"])
    op.create_index("ix_challenges_category", "challenges", ["category"])
    op.create_index("ix_challenges_difficulty", "challenges", ["difficulty"])

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_personal", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_teams_slug", "teams", ["slug"])

    op.create_table(
        "team_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", teamrole, nullable=False),
        sa.Column("invited_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("team_id", "user_id", name="uq_team_members_team_user"),
    )
    op.create_index("ix_team_members_team_id", "team_members", ["team_id"])
    op.create_index("ix_team_members_user_id", "team_members", ["user_id"])

    op.create_table(
        "team_invitations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("token", sa.String(64), nullable=False, unique=True),
        sa.Column("role", teamrole, nullable=False),
        sa.Column("invited_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_team_invitations_team_id", "team_invitations", ["team_id"])
    op.create_index("ix_team_invitations_token", "team_invitations", ["token"])

    # Created before deployments and challenge_submissions because both FK to it.
    op.create_table(
        "ctf_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", eventstatus, nullable=False, server_default="draft"),
        sa.Column("visibility", eventvisibility, nullable=False, server_default="private"),
        sa.Column("max_team_size", sa.Integer(), nullable=True),
        sa.Column("scoring_mode", eventscoringmode, nullable=False, server_default="static"),
        sa.Column("freeze_scoreboard_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ctf_events_slug", "ctf_events", ["slug"])
    op.create_index("ix_ctf_events_status", "ctf_events", ["status"])

    op.create_table(
        "deployments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lab_template_id", sa.Integer(), sa.ForeignKey("lab_templates.id"), nullable=False),
        sa.Column("started_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id"), nullable=True),
        sa.Column("instance_for_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", deploymentstatus, nullable=False),
        sa.Column("visibility", deploymentvisibility, nullable=False, server_default="private"),
        sa.Column("container_names", sa.JSON(), nullable=False),
        sa.Column("container_ids", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("dynamic_flag", sa.String(255), nullable=True),
        sa.Column("auto_destroy_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stopped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_deployments_lab_template_id", "deployments", ["lab_template_id"])
    op.create_index("ix_deployments_team_id", "deployments", ["team_id"])
    op.create_index("ix_deployments_challenge_id", "deployments", ["challenge_id"])
    op.create_index("ix_deployments_auto_destroy_at", "deployments", ["auto_destroy_at"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("deployment_id", sa.Integer(), sa.ForeignKey("deployments.id"), nullable=True),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("detail", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_team_id", "audit_logs", ["team_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("key_prefix", sa.String(12), nullable=False),
        sa.Column("hashed_key", sa.String(255), nullable=False),
        sa.Column("scopes", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"])

    op.create_table(
        "scheduled_actions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("lab_template_id", sa.Integer(), sa.ForeignKey("lab_templates.id"), nullable=True),
        sa.Column("deployment_id", sa.Integer(), sa.ForeignKey("deployments.id"), nullable=True),
        sa.Column("action", scheduledactiontype, nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", scheduledactionstatus, nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_scheduled_actions_user_id", "scheduled_actions", ["user_id"])
    op.create_index("ix_scheduled_actions_team_id", "scheduled_actions", ["team_id"])
    op.create_index("ix_scheduled_actions_scheduled_at", "scheduled_actions", ["scheduled_at"])

    op.create_table(
        "challenge_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("flag_type", flagtype, nullable=False, server_default="static"),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("regex_pattern", sa.Text(), nullable=True),
        sa.Column("hash_type", sa.String(16), nullable=True),
        sa.Column("validation_script", sa.Text(), nullable=True),
        sa.Column("case_sensitive", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_index("ix_challenge_flags_challenge_id", "challenge_flags", ["challenge_id"])

    op.create_table(
        "challenge_hints",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_num", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("challenge_id", "order_num", name="uq_challenge_hints_challenge_order"),
    )
    op.create_index("ix_challenge_hints_challenge_id", "challenge_hints", ["challenge_id"])

    op.create_table(
        "challenge_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(512), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=True),
    )
    op.create_index("ix_challenge_files_challenge_id", "challenge_files", ["challenge_id"])

    op.create_table(
        "challenge_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("ctf_events.id"), nullable=True),
        sa.Column("submitted_value", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_first_blood", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("points_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_challenge_submissions_challenge_id", "challenge_submissions", ["challenge_id"])
    op.create_index("ix_challenge_submissions_user_id", "challenge_submissions", ["user_id"])
    op.create_index("ix_challenge_submissions_event_id_team_id", "challenge_submissions", ["event_id", "team_id"])
    op.create_index("ix_challenge_submissions_submitted_at", "challenge_submissions", ["challenge_id", "submitted_at"])
    op.create_index(
        "uq_challenge_submissions_correct",
        "challenge_submissions",
        ["challenge_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("is_correct = true"),
    )

    op.create_table(
        "hint_unlocks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("hint_id", sa.Integer(), sa.ForeignKey("challenge_hints.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("hint_id", "user_id", name="uq_hint_unlocks_hint_user"),
    )
    op.create_index("ix_hint_unlocks_user_id", "hint_unlocks", ["user_id"])

    op.create_table(
        "score_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("ctf_events.id"), nullable=True),
        sa.Column("source_type", scoretransactionsource, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_score_transactions_user_id_event", "score_transactions", ["user_id", "event_id"])
    op.create_index("ix_score_transactions_team_id_event", "score_transactions", ["team_id", "event_id"])
    op.create_index("ix_score_transactions_created_at", "score_transactions", ["created_at"])

    op.create_table(
        "event_challenge_map",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("ctf_events.id"), nullable=False),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id"), nullable=False),
        sa.Column("points_override", sa.Integer(), nullable=True),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("event_id", "challenge_id", name="uq_event_challenge_map"),
    )
    op.create_index("ix_event_challenge_map_event_id", "event_challenge_map", ["event_id"])

    op.create_table(
        "event_registrations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("ctf_events.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("registered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("event_id", "team_id", name="uq_event_registrations"),
    )
    op.create_index("ix_event_registrations_event_id", "event_registrations", ["event_id"])

    op.create_table(
        "badge_definitions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("icon", sa.String(64), nullable=False, server_default="shield"),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("points_value", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "achievement_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("badge_id", sa.Integer(), sa.ForeignKey("badge_definitions.id"), nullable=False),
        sa.Column("rule_type", achievementruletype, nullable=False),
        sa.Column("rule_config", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_achievement_rules_badge_id", "achievement_rules", ["badge_id"])

    op.create_table(
        "user_badges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("badge_id", sa.Integer(), sa.ForeignKey("badge_definitions.id"), nullable=False),
        sa.Column("awarded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("awarded_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.UniqueConstraint("user_id", "badge_id", name="uq_user_badges"),
    )
    op.create_index("ix_user_badges_user_id", "user_badges", ["user_id"])

    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("website_url", sa.String(512), nullable=True),
        sa.Column("location", sa.String(128), nullable=True),
        sa.Column("github_handle", sa.String(64), nullable=True),
        sa.Column("twitter_handle", sa.String(64), nullable=True),
        sa.Column("privacy_level", privacylevel, nullable=False, server_default="public"),
        sa.Column("show_activity", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("data", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_user_read", "notifications", ["user_id", "read_at"])

    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("in_app", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("email", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("discord_webhook_url", sa.String(512), nullable=True),
        sa.Column("slack_webhook_url", sa.String(512), nullable=True),
        sa.Column("event_filter", sa.JSON(), nullable=False, server_default="{}"),
    )

    op.create_table(
        "content_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content_type", contenttype, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("status", contentstatus, nullable=False, server_default="draft"),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_content_submissions_author_id", "content_submissions", ["author_id"])
    op.create_index("ix_content_submissions_status", "content_submissions", ["status"])

    op.create_table(
        "content_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("submission_id", sa.Integer(), sa.ForeignKey("content_submissions.id"), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("verdict", reviewverdict, nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_content_reviews_submission_id", "content_reviews", ["submission_id"])

    op.create_table(
        "marketplace_packages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("package_type", packagetype, nullable=False),
        sa.Column("manifest", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("author", sa.String(128), nullable=True),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "package_installations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("package_id", sa.Integer(), sa.ForeignKey("marketplace_packages.id"), nullable=False),
        sa.Column("installed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_package_installations_package_id", "package_installations", ["package_id"])


def downgrade() -> None:
    op.drop_table("package_installations")
    op.drop_table("marketplace_packages")
    op.drop_table("content_reviews")
    op.drop_table("content_submissions")
    op.drop_table("notification_preferences")
    op.drop_table("notifications")
    op.drop_table("user_profiles")
    op.drop_table("user_badges")
    op.drop_table("achievement_rules")
    op.drop_table("badge_definitions")
    op.drop_table("event_registrations")
    op.drop_table("event_challenge_map")
    op.drop_table("score_transactions")
    op.drop_table("hint_unlocks")
    op.drop_table("challenge_submissions")
    op.drop_table("challenge_files")
    op.drop_table("challenge_hints")
    op.drop_table("challenge_flags")
    op.drop_table("scheduled_actions")
    op.drop_table("api_keys")
    op.drop_table("audit_logs")
    op.drop_table("deployments")
    op.drop_table("ctf_events")
    op.drop_table("team_invitations")
    op.drop_table("team_members")
    op.drop_table("teams")
    op.drop_table("challenges")
    op.drop_table("lab_templates")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS packagetype")
    op.execute("DROP TYPE IF EXISTS reviewverdict")
    op.execute("DROP TYPE IF EXISTS contentstatus")
    op.execute("DROP TYPE IF EXISTS contenttype")
    op.execute("DROP TYPE IF EXISTS privacylevel")
    op.execute("DROP TYPE IF EXISTS achievementruletype")
    op.execute("DROP TYPE IF EXISTS eventscoringmode")
    op.execute("DROP TYPE IF EXISTS eventvisibility")
    op.execute("DROP TYPE IF EXISTS eventstatus")
    op.execute("DROP TYPE IF EXISTS scoretransactionsource")
    op.execute("DROP TYPE IF EXISTS flagtype")
    op.execute("DROP TYPE IF EXISTS challengedifficulty")
    op.execute("DROP TYPE IF EXISTS challengetype")
    op.execute("DROP TYPE IF EXISTS scheduledactionstatus")
    op.execute("DROP TYPE IF EXISTS scheduledactiontype")
    op.execute("DROP TYPE IF EXISTS teamrole")
    op.execute("DROP TYPE IF EXISTS deploymentvisibility")
    op.execute("DROP TYPE IF EXISTS deploymentstatus")
