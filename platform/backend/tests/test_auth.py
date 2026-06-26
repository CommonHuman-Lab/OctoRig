# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Tests for /api/v1/auth/* — login, register, refresh, logout, /me,
change-password, and the brute-force lockout added alongside the role
system. No real DB, no real network — see tests/conftest.py.
"""

import os

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]


def _login(client, username, password):
    return client.post("/api/v1/auth/login", json={"username": username, "password": password})


def _register(
    client, username="newplayer", email="newplayer@example.com", password="StrongPassw0rd!"
):
    return client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )


# ── register ─────────────────────────────────────────────────────────────────


def test_register_success_returns_token_and_default_role(client):
    resp = _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    me_body = me.json()
    assert me_body["username"] == "newplayer"
    assert "player" in me_body["platform_roles"]
    assert "platform.dashboard" in me_body["permissions"]
    assert "admin.panel" not in me_body["permissions"]


def test_register_rejects_weak_password(client):
    resp = _register(client, password="short")
    assert resp.status_code == 400


def test_register_rejects_duplicate_username(client):
    assert _register(client, username="dupe", email="a@example.com").status_code == 201
    resp = _register(client, username="dupe", email="b@example.com")
    assert resp.status_code == 409


def test_register_rejects_duplicate_email(client):
    assert _register(client, username="user1", email="same@example.com").status_code == 201
    resp = _register(client, username="user2", email="same@example.com")
    assert resp.status_code == 409


def test_register_blocked_when_registration_closed(client):
    admin_token = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).json()["access_token"]
    patch = client.patch(
        "/api/v1/admin/settings",
        json={"registration_open": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch.status_code == 200

    resp = _register(client)
    assert resp.status_code == 403


# ── login ────────────────────────────────────────────────────────────────────


def test_login_success_with_seeded_admin(client):
    resp = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert "octorig_refresh_token" in resp.cookies


def test_login_wrong_password_rejected(client):
    resp = _login(client, ADMIN_USERNAME, "definitely-wrong")
    assert resp.status_code == 401


def test_login_unknown_username_rejected(client):
    resp = _login(client, "no-such-user", "whatever")
    assert resp.status_code == 401


def test_login_inactive_user_rejected(client):
    admin_token = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).json()["access_token"]
    _register(client, username="tobedeactivated", email="deact@example.com")

    users = client.get(
        "/api/v1/admin/users/",
        params={"search": "tobedeactivated"},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()
    user_id = users[0]["id"]

    deactivate = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert deactivate.status_code == 200

    resp = _login(client, "tobedeactivated", "StrongPassw0rd!")
    assert resp.status_code == 401


def test_login_lockout_after_repeated_failures(client):
    for _ in range(4):
        assert _login(client, ADMIN_USERNAME, "wrong").status_code == 401

    # 5th failure crosses the threshold and locks the account
    fifth = _login(client, ADMIN_USERNAME, "wrong")
    assert fifth.status_code == 401

    # Even the correct password is rejected while locked
    locked = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    assert locked.status_code == 429
    assert "locked" in locked.json()["detail"].lower()


def test_login_success_resets_failure_counter(client):
    for _ in range(3):
        assert _login(client, ADMIN_USERNAME, "wrong").status_code == 401

    assert _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).status_code == 200

    # Counter was reset, so three more failures shouldn't trip the 5-failure lock
    for _ in range(3):
        assert _login(client, ADMIN_USERNAME, "wrong").status_code == 401
    assert _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).status_code == 200


def test_admin_can_unlock_a_locked_account(client):
    admin_token = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).json()["access_token"]
    _register(client, username="lockme", email="lockme@example.com")

    for _ in range(5):
        _login(client, "lockme", "wrong")
    assert _login(client, "lockme", "StrongPassw0rd!").status_code == 429

    users = client.get(
        "/api/v1/admin/users/",
        params={"search": "lockme"},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()
    user_id = users[0]["id"]
    assert users[0]["locked_until"] is not None

    unlock = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"unlock": True},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert unlock.status_code == 200
    assert unlock.json()["locked_until"] is None

    assert _login(client, "lockme", "StrongPassw0rd!").status_code == 200


def test_login_rate_limited_per_ip(rate_limited_client):
    client = rate_limited_client
    statuses = [_login(client, ADMIN_USERNAME, "wrong").status_code for _ in range(6)]
    # First 5 attempts are evaluated normally (401); the 6th hits slowapi's cap
    assert statuses[:5] == [401] * 5
    assert statuses[5] == 429


# ── refresh / logout ─────────────────────────────────────────────────────────


def test_refresh_issues_new_access_token_and_rotates_cookie(client):
    login_resp = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    old_cookie = login_resp.cookies["octorig_refresh_token"]

    refresh_resp = client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()
    new_cookie = refresh_resp.cookies.get("octorig_refresh_token")
    assert new_cookie is not None
    assert new_cookie != old_cookie


def test_refresh_without_cookie_rejected(client):
    client.cookies.clear()
    resp = client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401


def test_refresh_rejects_revoked_token_after_rotation(client):
    login_resp = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    raw_token = login_resp.cookies["octorig_refresh_token"]

    client.post("/api/v1/auth/refresh")  # rotates it — raw_token is now revoked

    client.cookies.set("octorig_refresh_token", raw_token)
    replay = client.post("/api/v1/auth/refresh")
    assert replay.status_code == 401


def test_logout_revokes_refresh_token(client):
    login_resp = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    access_token = login_resp.json()["access_token"]

    logout_resp = client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_resp.status_code == 200

    refresh_resp = client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 401


# ── /me ──────────────────────────────────────────────────────────────────────


def test_me_requires_authentication(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_resolves_admin_permissions(client):
    token = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["platform_roles"] == ["admin"]
    assert "admin.panel" in body["permissions"]
    assert "creator.access" in body["permissions"]


# ── change-password ─────────────────────────────────────────────────────────


def test_change_password_success(client):
    token = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).json()["access_token"]
    resp = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": ADMIN_PASSWORD, "new_password": "New-Strong-Pw-1!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204

    assert _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).status_code == 401
    assert _login(client, ADMIN_USERNAME, "New-Strong-Pw-1!").status_code == 200


def test_change_password_rejects_wrong_current_password(client):
    token = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).json()["access_token"]
    resp = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "not-the-real-one", "new_password": "New-Strong-Pw-1!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_change_password_rejects_weak_new_password(client):
    token = _login(client, ADMIN_USERNAME, ADMIN_PASSWORD).json()["access_token"]
    resp = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": ADMIN_PASSWORD, "new_password": "short"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


# ── public settings ──────────────────────────────────────────────────────────


def test_public_settings_requires_no_auth(client):
    resp = client.get("/api/v1/auth/settings/public")
    assert resp.status_code == 200
    assert "registration_open" in resp.json()
