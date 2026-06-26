# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Unit tests for app.services.challenge_rendering — the {container_ip}
placeholder substitution used in challenge text and access_info, since the
registry no longer hardcodes a lab's IP (each deployment gets its own).
"""

from app.models.deployment import Deployment, DeploymentStatus
from app.models.lab_template import LabTemplate
from app.models.user import User
from app.services.challenge_rendering import render_access_info, render_target_text


def _user(db_session, username="alice"):
    user = User(username=username, email=f"{username}@example.com", hashed_password="x")
    db_session.add(user)
    db_session.commit()
    return user


def _template(db_session):
    return db_session.query(LabTemplate).filter(LabTemplate.slug == "medihuman").first()


def test_render_target_text_not_running_drops_backticks_and_links_to_lab(client, db_session):
    user = _user(db_session)
    template = _template(db_session)

    text = "**Target:** `http://{container_ip}/login`"
    rendered = render_target_text(text, db_session, user, template.id)

    assert "{container_ip}" not in rendered
    assert "`" not in rendered  # not wrapped in a now-meaningless code span
    assert f"[start {template.name}](/labs/{template.slug})" in rendered


def test_render_target_text_running_substitutes_real_ip_and_keeps_path(client, db_session):
    user = _user(db_session)
    template = _template(db_session)
    db_session.add(
        Deployment(
            lab_template_id=template.id,
            started_by_id=user.id,
            status=DeploymentStatus.RUNNING,
            container_names=[],
            subnet="10.90.5.0/24",
            app_ip="10.90.5.2",
        )
    )
    db_session.commit()

    text = "**Target:** `http://{container_ip}/login`"
    rendered = render_target_text(text, db_session, user, template.id)

    assert rendered == "**Target:** `http://10.90.5.2/login`"


def test_render_target_text_passthrough_without_placeholder(client, db_session):
    user = _user(db_session)
    assert render_target_text("no placeholder here", db_session, user, 1) == "no placeholder here"


def test_render_access_info_without_app_ip_collapses_to_not_running():
    entries = [{"key": "URL", "value": "http://{container_ip}"}]
    rendered = render_access_info(entries)
    assert rendered == [{"key": "URL", "value": "Not running"}]


def test_render_access_info_with_app_ip_substitutes_in_place():
    entries = [{"key": "SSH", "value": "ssh staff@{container_ip} (password: dragon)"}]
    rendered = render_access_info(entries, app_ip="10.90.5.2")
    assert rendered == [{"key": "SSH", "value": "ssh staff@10.90.5.2 (password: dragon)"}]


def test_render_access_info_leaves_non_placeholder_entries_untouched():
    entries = [{"key": "Login", "value": "admin / password"}]
    assert render_access_info(entries) == entries
