# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Tests for /api/v1/events/* — admin-only lifecycle management, the
visibility/listing rules, and the team-registration IDOR fix (a non-member
must not be able to register or unregister someone else's team). No real
DB, no real network — see tests/conftest.py.
"""
import os

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
PASSWORD = "StrongPassw0rd!"


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _admin_token(client):
    return client.post(
        "/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    ).json()["access_token"]


def _register_and_login(client, username):
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": PASSWORD},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def _create_event(client, admin_token, slug="test-event", **kwargs):
    payload = {
        "slug": slug,
        "title": "Test Event",
        "visibility": "public",
        "scoring_mode": "static",
        **kwargs,
    }
    resp = client.post("/api/v1/events/", json=payload, headers=_auth(admin_token))
    assert resp.status_code == 200, resp.text
    return resp.json()


def _publish(client, admin_token, slug):
    resp = client.post(
        f"/api/v1/events/{slug}/status", json={"status": "published"}, headers=_auth(admin_token)
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _create_team(client, token, name="Red Team"):
    resp = client.post("/api/v1/teams/", json={"name": name}, headers=_auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── admin-only gating ────────────────────────────────────────────────────────

def test_create_event_requires_admin(client):
    player_token = _register_and_login(client, "alice")
    resp = client.post(
        "/api/v1/events/",
        json={"slug": "x", "title": "X", "visibility": "public", "scoring_mode": "static"},
        headers=_auth(player_token),
    )
    assert resp.status_code == 403


def test_update_event_requires_admin(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)
    player_token = _register_and_login(client, "alice")

    resp = client.patch(
        "/api/v1/events/test-event", json={"title": "Hacked"}, headers=_auth(player_token)
    )
    assert resp.status_code == 403


def test_add_challenge_to_event_requires_admin(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)
    player_token = _register_and_login(client, "alice")

    resp = client.post(
        "/api/v1/events/test-event/challenges",
        json={"challenge_id": 1},
        headers=_auth(player_token),
    )
    assert resp.status_code == 403


# ── visibility / listing ─────────────────────────────────────────────────────

def test_private_event_hidden_from_regular_user_listing(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token, slug="secret-event", visibility="private")

    player_token = _register_and_login(client, "alice")
    resp = client.get("/api/v1/events/", headers=_auth(player_token))
    assert resp.status_code == 200
    assert "secret-event" not in {e["slug"] for e in resp.json()}


def test_private_event_visible_to_admin_listing(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token, slug="secret-event", visibility="private")

    resp = client.get("/api/v1/events/", headers=_auth(admin_token))
    assert "secret-event" in {e["slug"] for e in resp.json()}


def test_get_event_by_slug_works_for_any_authenticated_user(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)
    player_token = _register_and_login(client, "alice")

    resp = client.get("/api/v1/events/test-event", headers=_auth(player_token))
    assert resp.status_code == 200


def test_get_unknown_event_404(client):
    token = _register_and_login(client, "alice")
    resp = client.get("/api/v1/events/no-such-event", headers=_auth(token))
    assert resp.status_code == 404


# ── status transitions ──────────────────────────────────────────────────────

def test_draft_event_can_transition_to_published(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)

    resp = client.post(
        "/api/v1/events/test-event/status", json={"status": "published"}, headers=_auth(admin_token)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"


def test_invalid_status_transition_rejected(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)  # starts in draft

    resp = client.post(
        "/api/v1/events/test-event/status", json={"status": "ended"}, headers=_auth(admin_token)
    )
    assert resp.status_code == 400


# ── registration IDOR boundary ──────────────────────────────────────────────

def test_register_team_requires_membership(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)
    _publish(client, admin_token, "test-event")

    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)

    outsider_token = _register_and_login(client, "bob")
    resp = client.post(
        "/api/v1/events/test-event/register",
        json={"team_id": team["id"]},
        headers=_auth(outsider_token),
    )
    assert resp.status_code == 404


def test_register_own_team_succeeds(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)
    _publish(client, admin_token, "test-event")

    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)

    resp = client.post(
        "/api/v1/events/test-event/register",
        json={"team_id": team["id"]},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 200
    assert resp.json()["team_id"] == team["id"]


def test_register_rejected_before_event_is_published(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)  # still in draft

    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)

    resp = client.post(
        "/api/v1/events/test-event/register",
        json={"team_id": team["id"]},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 400


def test_unregister_team_requires_manager_role_not_just_membership(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)
    _publish(client, admin_token, "test-event")

    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    client.post(
        "/api/v1/events/test-event/register", json={"team_id": team["id"]}, headers=_auth(owner_token)
    )

    member_token = _register_and_login(client, "bob")
    invite = client.post(
        f"/api/v1/teams/{team['id']}/invite",
        json={"username": "bob", "role": "member"},
        headers=_auth(owner_token),
    ).json()
    client.post(f"/api/v1/invitations/{invite['token']}/accept", headers=_auth(member_token))

    resp = client.delete(
        f"/api/v1/events/test-event/register/{team['id']}", headers=_auth(member_token)
    )
    assert resp.status_code == 403


def test_unregister_team_allowed_for_owner(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)
    _publish(client, admin_token, "test-event")

    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    client.post(
        "/api/v1/events/test-event/register", json={"team_id": team["id"]}, headers=_auth(owner_token)
    )

    resp = client.delete(
        f"/api/v1/events/test-event/register/{team['id']}", headers=_auth(owner_token)
    )
    assert resp.status_code == 204


def test_unrelated_user_cannot_unregister_someone_elses_team(client):
    """The IDOR this module was specifically fixed for: registering/unregistering
    an arbitrary team_id you have no relationship to."""
    admin_token = _admin_token(client)
    _create_event(client, admin_token)
    _publish(client, admin_token, "test-event")

    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    client.post(
        "/api/v1/events/test-event/register", json={"team_id": team["id"]}, headers=_auth(owner_token)
    )

    outsider_token = _register_and_login(client, "bob")
    resp = client.delete(
        f"/api/v1/events/test-event/register/{team['id']}", headers=_auth(outsider_token)
    )
    assert resp.status_code == 404


def test_admin_can_register_and_unregister_any_team(client):
    admin_token = _admin_token(client)
    _create_event(client, admin_token)
    _publish(client, admin_token, "test-event")

    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)

    reg = client.post(
        "/api/v1/events/test-event/register", json={"team_id": team["id"]}, headers=_auth(admin_token)
    )
    assert reg.status_code == 200

    unreg = client.delete(
        f"/api/v1/events/test-event/register/{team['id']}", headers=_auth(admin_token)
    )
    assert unreg.status_code == 204
