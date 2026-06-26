# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Tests for /api/v1/admin/* — user management, teams/deployments visibility
across all users, audit logs, API keys, stats, and the destructive
reset-points / reset-db endpoints. No real DB, no real network, no real
Docker — see tests/conftest.py.
"""

import os

from app.models.deployment import Deployment, DeploymentStatus

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


def _user_id(client, token):
    return client.get("/api/v1/auth/me", headers=_auth(token)).json()["id"]


def _admin_id(client, admin_token):
    return _user_id(client, admin_token)


# ── access control ───────────────────────────────────────────────────────────


def test_admin_endpoints_require_admin(client):
    player_token = _register_and_login(client, "alice")
    cases = [
        ("get", "/api/v1/admin/stats"),
        ("get", "/api/v1/admin/users/"),
        ("get", "/api/v1/admin/teams/"),
        ("get", "/api/v1/admin/deployments/"),
        ("get", "/api/v1/admin/audit-logs/"),
        ("get", "/api/v1/admin/api-keys/"),
    ]
    for method, path in cases:
        resp = getattr(client, method)(path, headers=_auth(player_token))
        assert resp.status_code == 403, f"{method} {path} should be admin-only"


# ── stats ────────────────────────────────────────────────────────────────────


def test_stats_reflects_seeded_admin(client):
    token = _admin_token(client)
    resp = client.get("/api/v1/admin/stats", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["user_count"] == 1


# ── user management ──────────────────────────────────────────────────────────


def test_admin_create_user_success(client):
    token = _admin_token(client)
    resp = client.post(
        "/api/v1/admin/users/",
        json={"username": "newuser", "email": "newuser@example.com", "password": "irrelevant"},
        headers=_auth(token),
    )
    assert resp.status_code == 201
    assert resp.json()["platform_roles"] == []


def test_admin_create_user_rejects_duplicate_username(client):
    token = _admin_token(client)
    client.post(
        "/api/v1/admin/users/",
        json={"username": "dupe", "email": "a@example.com", "password": "x"},
        headers=_auth(token),
    )
    resp = client.post(
        "/api/v1/admin/users/",
        json={"username": "dupe", "email": "b@example.com", "password": "x"},
        headers=_auth(token),
    )
    assert resp.status_code == 409


def test_list_users_search_filters_by_username(client):
    token = _admin_token(client)
    _register_and_login(client, "findme")
    _register_and_login(client, "someoneelse")

    resp = client.get("/api/v1/admin/users/", params={"search": "findme"}, headers=_auth(token))
    assert resp.status_code == 200
    usernames = {u["username"] for u in resp.json()}
    assert usernames == {"findme"}


def test_admin_cannot_deactivate_own_account(client):
    token = _admin_token(client)
    admin_id = _admin_id(client, token)
    resp = client.patch(
        f"/api/v1/admin/users/{admin_id}", json={"is_active": False}, headers=_auth(token)
    )
    assert resp.status_code == 400


def test_admin_can_deactivate_other_account(client):
    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    user_id = _user_id(client, player_token)

    resp = client.patch(
        f"/api/v1/admin/users/{user_id}", json={"is_active": False}, headers=_auth(admin_token)
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_seeded_admin_is_marked_owner(client):
    admin_token = _admin_token(client)
    admin_id = _admin_id(client, admin_token)
    users = client.get("/api/v1/admin/users/", headers=_auth(admin_token)).json()
    seeded = next(u for u in users if u["id"] == admin_id)
    assert seeded["is_owner"] is True


def test_owner_cannot_be_deactivated_even_by_another_admin(client):
    """Ownership is a stronger protection than the regular admin role: it
    must hold even when a second active admin exists, which rules out the
    last-remaining-admin guard as the explanation for the 400."""
    admin_token = _admin_token(client)
    admin_id = _admin_id(client, admin_token)

    second_token = _register_and_login(client, "second_admin")
    second_id = _user_id(client, second_token)
    client.patch(
        f"/api/v1/admin/users/{second_id}",
        json={"platform_roles": ["admin"]},
        headers=_auth(admin_token),
    )

    resp = client.patch(
        f"/api/v1/admin/users/{admin_id}", json={"is_active": False}, headers=_auth(second_token)
    )
    assert resp.status_code == 400


def test_owner_roles_cannot_be_changed_by_another_admin(client):
    admin_token = _admin_token(client)
    admin_id = _admin_id(client, admin_token)

    second_token = _register_and_login(client, "second_admin")
    second_id = _user_id(client, second_token)
    client.patch(
        f"/api/v1/admin/users/{second_id}",
        json={"platform_roles": ["admin"]},
        headers=_auth(admin_token),
    )

    resp = client.patch(
        f"/api/v1/admin/users/{admin_id}",
        json={"platform_roles": ["player"]},
        headers=_auth(second_token),
    )
    assert resp.status_code == 400


def test_cannot_deactivate_last_remaining_admin(client):
    """A non-admin actor with just enough delegated permission to reach this
    endpoint must still be blocked from deactivating the sole remaining
    'admin'-role account — otherwise the panel becomes permanently
    inaccessible with no recovery path. This is distinct from the
    self-deactivation guard: the actor here is a different user."""
    admin_token = _admin_token(client)
    admin_id = _admin_id(client, admin_token)

    client.post(
        "/api/v1/admin/roles/",
        json={
            "slug": "ops",
            "display_name": "Ops",
            "permissions": ["admin.panel", "admin.users.manage"],
        },
        headers=_auth(admin_token),
    )
    helper_token = _register_and_login(client, "helper")
    helper_id = _user_id(client, helper_token)
    client.patch(
        f"/api/v1/admin/users/{helper_id}",
        json={"platform_roles": ["ops"]},
        headers=_auth(admin_token),
    )

    resp = client.patch(
        f"/api/v1/admin/users/{admin_id}", json={"is_active": False}, headers=_auth(helper_token)
    )
    assert resp.status_code == 400


def test_admin_reset_password_takes_effect(client):
    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    user_id = _user_id(client, player_token)

    resp = client.post(
        f"/api/v1/admin/users/{user_id}/reset-password",
        json={"new_password": "Brand-New-Pw-1!"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 204

    old_login = client.post("/api/v1/auth/login", json={"username": "alice", "password": PASSWORD})
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login", json={"username": "alice", "password": "Brand-New-Pw-1!"}
    )
    assert new_login.status_code == 200


def test_admin_reset_points_clears_submissions(client, db_session):
    from app.models.scoring import ScoreTransaction, ScoreTransactionSource

    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    user_id = _user_id(client, player_token)

    db_session.add(
        ScoreTransaction(
            user_id=user_id, points=100, source_type=ScoreTransactionSource.CHALLENGE_SOLVE
        )
    )
    db_session.commit()
    assert db_session.query(ScoreTransaction).filter_by(user_id=user_id).count() == 1

    resp = client.post(f"/api/v1/admin/users/{user_id}/reset-points", headers=_auth(admin_token))
    assert resp.status_code == 204
    assert db_session.query(ScoreTransaction).filter_by(user_id=user_id).count() == 0


def test_get_unknown_user_404(client):
    token = _admin_token(client)
    resp = client.get("/api/v1/admin/users/999999", headers=_auth(token))
    assert resp.status_code == 404


# ── reset-db ─────────────────────────────────────────────────────────────────


def test_reset_db_wipes_activity_but_keeps_accounts(client, db_session):
    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    template_id = client.get("/api/v1/labs/", headers=_auth(player_token)).json()[0]["id"]
    client.post(
        "/api/v1/deployments/",
        json={"lab_template_id": template_id},
        headers=_auth(player_token),
    )
    assert db_session.query(Deployment).count() >= 1

    resp = client.post("/api/v1/admin/reset-db", headers=_auth(admin_token))
    assert resp.status_code == 204

    assert db_session.query(Deployment).count() == 0
    # accounts survive
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "alice", "password": PASSWORD}
        ).status_code
        == 200
    )


# ── teams / deployments (cross-user visibility) ─────────────────────────────


def test_admin_lists_all_teams_including_personal(client):
    token = _admin_token(client)
    _register_and_login(client, "alice")

    resp = client.get("/api/v1/admin/teams/", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_admin_lists_deployments_across_all_users(client):
    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    template_id = client.get("/api/v1/labs/", headers=_auth(player_token)).json()[0]["id"]
    client.post(
        "/api/v1/deployments/", json={"lab_template_id": template_id}, headers=_auth(player_token)
    )

    resp = client.get("/api/v1/admin/deployments/", headers=_auth(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_stop_all_deployments_transitions_active_to_stopping(client, db_session):
    import app.services.lab_service as lab_service

    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    template_id = client.get("/api/v1/labs/", headers=_auth(player_token)).json()[0]["id"]
    body = client.post(
        "/api/v1/deployments/", json={"lab_template_id": template_id}, headers=_auth(player_token)
    ).json()

    d = db_session.get(Deployment, body["id"])
    d.status = DeploymentStatus.RUNNING
    db_session.commit()

    resp = client.post("/api/v1/admin/deployments/stop-all", headers=_auth(admin_token))
    assert resp.status_code == 204

    db_session.expire_all()
    assert db_session.get(Deployment, body["id"]).status == DeploymentStatus.STOPPING
    assert lab_service.stop_lab.called  # never touches real Docker


def test_restart_platform_stops_active_deployments_and_restarts_containers(client, db_session):
    import app.services.lab_service as lab_service
    from app.services.docker_runtime import docker_service

    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    template_id = client.get("/api/v1/labs/", headers=_auth(player_token)).json()[0]["id"]
    body = client.post(
        "/api/v1/deployments/", json={"lab_template_id": template_id}, headers=_auth(player_token)
    ).json()

    d = db_session.get(Deployment, body["id"])
    d.status = DeploymentStatus.RUNNING
    db_session.commit()

    resp = client.post("/api/v1/admin/platform/restart", headers=_auth(admin_token))
    assert resp.status_code == 202

    db_session.expire_all()
    assert db_session.get(Deployment, body["id"]).status == DeploymentStatus.STOPPING
    assert lab_service.stop_lab.called  # never touches real Docker
    assert docker_service.restart_container.called
    assert docker_service.restart_container.call_count == 4  # api, worker, beat, ui


def test_restart_platform_requires_admin(client):
    player_token = _register_and_login(client, "alice")
    resp = client.post("/api/v1/admin/platform/restart", headers=_auth(player_token))
    assert resp.status_code == 403


# ── audit logs ───────────────────────────────────────────────────────────────


def test_audit_logs_record_login_events(client):
    admin_token = _admin_token(client)
    resp = client.get(
        "/api/v1/admin/audit-logs/", params={"action": "auth.login"}, headers=_auth(admin_token)
    )
    assert resp.status_code == 200
    assert any(log["action"] == "auth.login" for log in resp.json())


def test_audit_logs_filter_by_user_id(client):
    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")
    user_id = _user_id(client, player_token)

    resp = client.get(
        "/api/v1/admin/audit-logs/", params={"user_id": user_id}, headers=_auth(admin_token)
    )
    assert resp.status_code == 200
    assert all(log["user_id"] == user_id for log in resp.json())
    assert len(resp.json()) >= 1


# ── api keys ─────────────────────────────────────────────────────────────────


def test_admin_lists_and_revokes_api_keys(client):
    admin_token = _admin_token(client)
    player_token = _register_and_login(client, "alice")

    created = client.post("/api/v1/api-keys/", json={"name": "ci-key"}, headers=_auth(player_token))
    assert created.status_code == 201
    key_id = created.json()["id"]

    listing = client.get("/api/v1/admin/api-keys/", headers=_auth(admin_token))
    assert listing.status_code == 200
    assert any(k["id"] == key_id for k in listing.json())

    revoke = client.delete(f"/api/v1/admin/api-keys/{key_id}", headers=_auth(admin_token))
    assert revoke.status_code == 204

    still_active = client.get(
        "/api/v1/admin/api-keys/", params={"active_only": True}, headers=_auth(admin_token)
    )
    assert all(k["id"] != key_id for k in still_active.json())
