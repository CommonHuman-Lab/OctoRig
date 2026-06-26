# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Tests for /api/v1/admin/roles/* and the platform_roles assignment endpoint
on /api/v1/admin/users/{id} — the configurable RBAC system that replaced the
old is_admin/is_superuser flags. No real DB, no real network — see
tests/conftest.py.
"""

import os

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
PASSWORD = "StrongPassw0rd!"

SEEDED_SLUGS = {"admin", "creator", "player", "viewer"}


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


def _user_id(client, token):
    return client.get("/api/v1/auth/me", headers=_auth(token)).json()["id"]


# ── access control ───────────────────────────────────────────────────────────


def test_roles_endpoints_require_admin(client):
    player_token = _register_and_login(client, "alice")
    cases = [
        ("get", "/api/v1/admin/roles/", {}),
        ("post", "/api/v1/admin/roles/", {"json": {}}),
        ("get", "/api/v1/admin/roles/player", {}),
        ("patch", "/api/v1/admin/roles/player", {"json": {}}),
        ("delete", "/api/v1/admin/roles/player", {}),
    ]
    for method, path, kwargs in cases:
        resp = getattr(client, method)(path, headers=_auth(player_token), **kwargs)
        assert resp.status_code == 403, f"{method} {path} should be admin-only"


def test_roles_endpoints_require_authentication(client):
    resp = client.get("/api/v1/admin/roles/")
    assert resp.status_code == 401


# ── seeded system roles ──────────────────────────────────────────────────────


def test_seeded_system_roles_present(client):
    token = _admin_token(client)
    resp = client.get("/api/v1/admin/roles/", headers=_auth(token))
    assert resp.status_code == 200
    roles = {r["slug"]: r for r in resp.json()}
    assert SEEDED_SLUGS <= roles.keys()
    assert roles["admin"]["is_system"] is True
    assert roles["player"]["is_default"] is True
    assert "admin.panel" in roles["admin"]["permissions"]
    assert "platform.dashboard" in roles["player"]["permissions"]


# ── CRUD ─────────────────────────────────────────────────────────────────────


def test_create_custom_role(client):
    token = _admin_token(client)
    resp = client.post(
        "/api/v1/admin/roles/",
        json={
            "slug": "support",
            "display_name": "Support",
            "description": "Read-only support staff",
            "permissions": ["platform.dashboard", "admin.users.view"],
        },
        headers=_auth(token),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["is_system"] is False
    assert body["is_default"] is False
    assert set(body["permissions"]) == {"platform.dashboard", "admin.users.view"}


def test_create_role_rejects_duplicate_slug(client):
    token = _admin_token(client)
    resp = client.post(
        "/api/v1/admin/roles/",
        json={"slug": "player", "display_name": "Dupe", "permissions": []},
        headers=_auth(token),
    )
    assert resp.status_code == 409


def test_create_role_rejects_invalid_slug(client):
    token = _admin_token(client)
    resp = client.post(
        "/api/v1/admin/roles/",
        json={"slug": "Not A Slug!", "display_name": "Bad", "permissions": []},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_get_unknown_role_404(client):
    token = _admin_token(client)
    resp = client.get("/api/v1/admin/roles/does-not-exist", headers=_auth(token))
    assert resp.status_code == 404


def test_update_role_permissions(client):
    token = _admin_token(client)
    resp = client.patch(
        "/api/v1/admin/roles/viewer",
        json={"permissions": ["platform.dashboard"]},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["permissions"] == ["platform.dashboard"]


def test_delete_custom_role(client):
    token = _admin_token(client)
    client.post(
        "/api/v1/admin/roles/",
        json={"slug": "throwaway", "display_name": "Throwaway", "permissions": []},
        headers=_auth(token),
    )
    resp = client.delete("/api/v1/admin/roles/throwaway", headers=_auth(token))
    assert resp.status_code == 204
    assert client.get("/api/v1/admin/roles/throwaway", headers=_auth(token)).status_code == 404


def test_cannot_delete_system_role(client):
    token = _admin_token(client)
    resp = client.delete("/api/v1/admin/roles/admin", headers=_auth(token))
    assert resp.status_code == 400


def test_cannot_edit_admin_role(client):
    """The admin role must stay untouchable — editing it (e.g. stripping
    admin.panel) could lock every admin out of the panel with no recovery path."""
    token = _admin_token(client)
    resp = client.patch(
        "/api/v1/admin/roles/admin",
        json={"permissions": ["platform.dashboard"]},
        headers=_auth(token),
    )
    assert resp.status_code == 400
    assert (
        "admin.panel"
        in client.get("/api/v1/admin/roles/admin", headers=_auth(token)).json()["permissions"]
    )


def test_delete_unknown_role_404(client):
    token = _admin_token(client)
    resp = client.delete("/api/v1/admin/roles/does-not-exist", headers=_auth(token))
    assert resp.status_code == 404


# ── assigning roles to users (PATCH /admin/users/{id}) ─────────────────────


def test_admin_can_assign_roles_to_user(client):
    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    user_id = _user_id(client, player_token)

    resp = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"platform_roles": ["player", "creator"]},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 200
    assert set(resp.json()["platform_roles"]) == {"player", "creator"}

    me = client.get("/api/v1/auth/me", headers=_auth(player_token)).json()
    assert "creator.access" in me["permissions"]


def test_admin_cannot_change_own_roles(client):
    """Self-demotion (e.g. dropping your own 'admin' role) must be blocked —
    otherwise an admin could lock themselves out with no one left to fix it."""
    admin_token = _admin_token(client)
    admin_id = _user_id(client, admin_token)
    resp = client.patch(
        f"/api/v1/admin/users/{admin_id}",
        json={"platform_roles": ["player"]},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 400


def test_assigning_unknown_role_slug_rejected(client):
    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    user_id = _user_id(client, player_token)

    resp = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"platform_roles": ["not-a-real-role"]},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 400


def test_custom_role_with_admin_panel_grants_admin_access(client):
    """End-to-end: a non-system role carrying admin.panel must pass require_admin,
    proving permission resolution — not just the is_admin flag — drives access."""
    admin_token = _admin_token(client)
    client.post(
        "/api/v1/admin/roles/",
        json={
            "slug": "support-admin",
            "display_name": "Support Admin",
            "permissions": ["admin.panel", "admin.users.view"],
        },
        headers=_auth(admin_token),
    )

    helper_token = _register_and_login(client, "helper")
    user_id = _user_id(client, helper_token)
    client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"platform_roles": ["support-admin"]},
        headers=_auth(admin_token),
    )

    resp = client.get("/api/v1/admin/roles/", headers=_auth(helper_token))
    assert resp.status_code == 200


def test_player_without_admin_panel_still_denied_admin_routes(client):
    player_token = _register_and_login(client, "alice")
    resp = client.get("/api/v1/admin/roles/", headers=_auth(player_token))
    assert resp.status_code == 403
