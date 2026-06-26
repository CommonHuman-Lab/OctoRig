# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Tests for /api/v1/notifications/* — listing, read/unread state, ownership
boundaries on delete, and preference-based suppression. No real DB, no real
network — see tests/conftest.py.
"""

from app.models.notification import Notification

PASSWORD = "StrongPassw0rd!"


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _register_and_login(client, username):
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": PASSWORD},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def _user_id(client, token):
    return client.get("/api/v1/auth/me", headers=_auth(token)).json()["id"]


def _add_notification(db_session, user_id, type_="generic", title="Hello"):
    n = Notification(user_id=user_id, type=type_, title=title)
    db_session.add(n)
    db_session.commit()
    db_session.refresh(n)
    return n


# ── access control ───────────────────────────────────────────────────────────


def test_notifications_require_authentication(client):
    assert client.get("/api/v1/notifications/").status_code == 401
    assert client.get("/api/v1/notifications/unread-count").status_code == 401


# ── listing ──────────────────────────────────────────────────────────────────


def test_list_returns_only_own_notifications(client, db_session):
    alice_token = _register_and_login(client, "alice")
    bob_token = _register_and_login(client, "bob")
    _add_notification(db_session, _user_id(client, alice_token), title="For Alice")
    _add_notification(db_session, _user_id(client, bob_token), title="For Bob")

    resp = client.get("/api/v1/notifications/", headers=_auth(alice_token))
    assert resp.status_code == 200
    titles = {n["title"] for n in resp.json()}
    assert titles == {"For Alice"}


def test_unread_only_filter(client, db_session):
    token = _register_and_login(client, "alice")
    user_id = _user_id(client, token)
    _add_notification(db_session, user_id, title="Unread")
    n2 = _add_notification(db_session, user_id, title="Read")
    client.post(f"/api/v1/notifications/{n2.id}/read", headers=_auth(token))

    resp = client.get("/api/v1/notifications/", params={"unread_only": True}, headers=_auth(token))
    assert resp.status_code == 200
    titles = {n["title"] for n in resp.json()}
    assert titles == {"Unread"}


def test_unread_count(client, db_session):
    token = _register_and_login(client, "alice")
    user_id = _user_id(client, token)
    _add_notification(db_session, user_id)
    _add_notification(db_session, user_id)

    resp = client.get("/api/v1/notifications/unread-count", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["count"] == 2


# ── read state ───────────────────────────────────────────────────────────────


def test_mark_single_notification_read(client, db_session):
    token = _register_and_login(client, "alice")
    n = _add_notification(db_session, _user_id(client, token))

    resp = client.post(f"/api/v1/notifications/{n.id}/read", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    db_session.refresh(n)
    assert n.read_at is not None


def test_mark_read_on_someone_elses_notification_is_a_noop(client, db_session):
    alice_token = _register_and_login(client, "alice")
    bob_token = _register_and_login(client, "bob")
    n = _add_notification(db_session, _user_id(client, alice_token))

    resp = client.post(f"/api/v1/notifications/{n.id}/read", headers=_auth(bob_token))
    assert resp.status_code == 200
    assert resp.json()["ok"] is False

    db_session.refresh(n)
    assert n.read_at is None


def test_mark_all_read_only_affects_caller(client, db_session):
    alice_token = _register_and_login(client, "alice")
    bob_token = _register_and_login(client, "bob")
    _add_notification(db_session, _user_id(client, alice_token))
    _add_notification(db_session, _user_id(client, alice_token))
    _add_notification(db_session, _user_id(client, bob_token))

    resp = client.post("/api/v1/notifications/read-all", headers=_auth(alice_token))
    assert resp.status_code == 200
    assert resp.json()["marked"] == 2

    bob_unread = client.get("/api/v1/notifications/unread-count", headers=_auth(bob_token)).json()
    assert bob_unread["count"] == 1


# ── delete / ownership ──────────────────────────────────────────────────────


def test_delete_own_notification(client, db_session):
    token = _register_and_login(client, "alice")
    n = _add_notification(db_session, _user_id(client, token))

    resp = client.delete(f"/api/v1/notifications/{n.id}", headers=_auth(token))
    assert resp.status_code == 204
    db_session.expunge_all()
    assert db_session.query(Notification).filter_by(id=n.id).first() is None


def test_cannot_delete_someone_elses_notification(client, db_session):
    alice_token = _register_and_login(client, "alice")
    bob_token = _register_and_login(client, "bob")
    n = _add_notification(db_session, _user_id(client, alice_token))

    resp = client.delete(f"/api/v1/notifications/{n.id}", headers=_auth(bob_token))
    assert resp.status_code == 204  # idempotent no-op, doesn't leak existence
    assert db_session.get(Notification, n.id) is not None


# ── preferences ──────────────────────────────────────────────────────────────


def test_get_preferences_creates_sane_defaults(client):
    token = _register_and_login(client, "alice")
    resp = client.get("/api/v1/notifications/preferences", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["in_app"] is True
    assert body["email"] is False


def test_update_preferences_partial(client):
    token = _register_and_login(client, "alice")
    resp = client.patch(
        "/api/v1/notifications/preferences",
        json={"email": True, "discord_webhook_url": "https://discord.example/webhook"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] is True
    assert body["discord_webhook_url"] == "https://discord.example/webhook"
    assert body["in_app"] is True  # untouched field preserved


def test_disabling_in_app_suppresses_new_notifications(client):
    """End-to-end via the real notification-producing path (team invites),
    not a direct DB insert — proves the preference actually gates delivery."""
    owner_token = _register_and_login(client, "alice")
    team = client.post(
        "/api/v1/teams/", json={"name": "Red Team"}, headers=_auth(owner_token)
    ).json()

    member_token = _register_and_login(client, "bob")
    client.patch(
        "/api/v1/notifications/preferences", json={"in_app": False}, headers=_auth(member_token)
    )

    client.post(
        f"/api/v1/teams/{team['id']}/invite",
        json={"username": "bob", "role": "member"},
        headers=_auth(owner_token),
    )

    resp = client.get("/api/v1/notifications/", headers=_auth(member_token))
    assert resp.status_code == 200
    assert resp.json() == []


def test_event_filter_suppresses_specific_notification_type(client):
    owner_token = _register_and_login(client, "alice")
    team = client.post(
        "/api/v1/teams/", json={"name": "Red Team"}, headers=_auth(owner_token)
    ).json()

    member_token = _register_and_login(client, "bob")
    client.patch(
        "/api/v1/notifications/preferences",
        json={"event_filter": {"team_invite": False}},
        headers=_auth(member_token),
    )

    client.post(
        f"/api/v1/teams/{team['id']}/invite",
        json={"username": "bob", "role": "member"},
        headers=_auth(owner_token),
    )

    resp = client.get("/api/v1/notifications/", headers=_auth(member_token))
    assert resp.json() == []
