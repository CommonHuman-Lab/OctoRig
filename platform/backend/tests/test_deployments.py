# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Tests for /api/v1/deployments/* — visibility, ownership, and team-role
authorization boundaries. Docker is never touched: the autouse `no_docker`
fixture in conftest.py stubs out lab_service.start_lab/stop_lab/reset_lab,
so deployments stay in their initial DB state ("starting") for the duration
of a test. No real DB, no real network, no real Docker — see
tests/conftest.py.
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


def _any_lab_template_id(client, token):
    labs = client.get("/api/v1/labs/", headers=_auth(token)).json()
    assert labs, "no lab templates were seeded at startup"
    return labs[0]["id"]


def _firerange_lab_template_id(client, token):
    labs = client.get("/api/v1/labs/", params={"category": "firerange"}, headers=_auth(token)).json()
    assert labs, "no firerange lab templates were seeded at startup"
    return labs[0]["id"]


def _deploy(client, token, lab_template_id=None, **kwargs):
    payload = {"lab_template_id": lab_template_id, **kwargs} if lab_template_id else kwargs
    resp = client.post("/api/v1/deployments/", json=payload, headers=_auth(token))
    assert resp.status_code == 202, resp.text
    return resp.json()


def _force_running(db_session, deployment_id):
    d = db_session.get(Deployment, deployment_id)
    d.status = DeploymentStatus.RUNNING
    db_session.commit()


# ── guard: prove Docker is never actually touched ───────────────────────────

def test_deployment_creation_never_calls_real_docker(client):
    """Asserts the autouse no_docker mock actually intercepted the
    BackgroundTask call — not just that nothing crashed. If this ever starts
    failing, deployment tests may be silently hitting a real Docker socket."""
    import app.services.lab_service as lab_service

    token = _register_and_login(client, "alice")
    _deploy(client, token, lab_template_id=_any_lab_template_id(client, token))

    assert lab_service.start_lab.called
    args = lab_service.start_lab.call_args.args
    assert isinstance(args[0], int)  # deployment_id was passed through as usual


# ── create ───────────────────────────────────────────────────────────────────

def test_create_deployment_success(client):
    token = _register_and_login(client, "alice")
    template_id = _any_lab_template_id(client, token)

    body = _deploy(client, token, lab_template_id=template_id)
    me = client.get("/api/v1/auth/me", headers=_auth(token)).json()
    assert body["started_by_id"] == me["id"]
    assert body["status"] == "starting"
    assert body["visibility"] == "private"


def test_create_deployment_to_foreign_team_rejected(client):
    owner_token = _register_and_login(client, "alice")
    team = client.post("/api/v1/teams/", json={"name": "Red Team"}, headers=_auth(owner_token)).json()

    outsider_token = _register_and_login(client, "bob")
    template_id = _any_lab_template_id(client, outsider_token)
    resp = client.post(
        "/api/v1/deployments/",
        json={"lab_template_id": template_id, "team_id": team["id"]},
        headers=_auth(outsider_token),
    )
    assert resp.status_code == 404


def test_create_deployment_to_own_team_succeeds(client):
    token = _register_and_login(client, "alice")
    team = client.post("/api/v1/teams/", json={"name": "Red Team"}, headers=_auth(token)).json()
    template_id = _any_lab_template_id(client, token)

    resp = client.post(
        "/api/v1/deployments/",
        json={"lab_template_id": template_id, "team_id": team["id"]},
        headers=_auth(token),
    )
    assert resp.status_code == 202
    assert resp.json()["team_id"] == team["id"]


def test_create_deployment_requires_template_or_challenge(client):
    token = _register_and_login(client, "alice")
    resp = client.post("/api/v1/deployments/", json={}, headers=_auth(token))
    assert resp.status_code == 422


# ── visibility / get ─────────────────────────────────────────────────────────

def test_owner_can_view_own_deployment(client):
    token = _register_and_login(client, "alice")
    body = _deploy(client, token, lab_template_id=_any_lab_template_id(client, token))

    resp = client.get(f"/api/v1/deployments/{body['id']}", headers=_auth(token))
    assert resp.status_code == 200


def test_unrelated_user_cannot_view_private_deployment(client):
    owner_token = _register_and_login(client, "alice")
    body = _deploy(client, owner_token, lab_template_id=_any_lab_template_id(client, owner_token))

    outsider_token = _register_and_login(client, "bob")
    resp = client.get(f"/api/v1/deployments/{body['id']}", headers=_auth(outsider_token))
    assert resp.status_code == 404  # existence not leaked


def test_public_deployment_visible_to_anyone_authenticated(client):
    owner_token = _register_and_login(client, "alice")
    template_id = _any_lab_template_id(client, owner_token)
    body = _deploy(client, owner_token, lab_template_id=template_id, visibility="public")

    outsider_token = _register_and_login(client, "bob")
    resp = client.get(f"/api/v1/deployments/{body['id']}", headers=_auth(outsider_token))
    assert resp.status_code == 200


def test_team_visible_deployment_requires_membership(client):
    owner_token = _register_and_login(client, "alice")
    team = client.post("/api/v1/teams/", json={"name": "Red Team"}, headers=_auth(owner_token)).json()
    template_id = _any_lab_template_id(client, owner_token)
    body = _deploy(
        client, owner_token, lab_template_id=template_id, team_id=team["id"], visibility="team"
    )

    outsider_token = _register_and_login(client, "bob")
    denied = client.get(f"/api/v1/deployments/{body['id']}", headers=_auth(outsider_token))
    assert denied.status_code == 404

    invite = client.post(
        f"/api/v1/teams/{team['id']}/invite",
        json={"username": "bob", "role": "member"},
        headers=_auth(owner_token),
    ).json()
    client.post(f"/api/v1/invitations/{invite['token']}/accept", headers=_auth(outsider_token))

    allowed = client.get(f"/api/v1/deployments/{body['id']}", headers=_auth(outsider_token))
    assert allowed.status_code == 200


def test_admin_can_view_any_deployment(client):
    owner_token = _register_and_login(client, "alice")
    body = _deploy(client, owner_token, lab_template_id=_any_lab_template_id(client, owner_token))

    admin_token = _admin_token(client)
    resp = client.get(f"/api/v1/deployments/{body['id']}", headers=_auth(admin_token))
    assert resp.status_code == 200


def test_list_deployments_excludes_others_private_deployments(client):
    owner_token = _register_and_login(client, "alice")
    _deploy(client, owner_token, lab_template_id=_any_lab_template_id(client, owner_token))

    outsider_token = _register_and_login(client, "bob")
    resp = client.get("/api/v1/deployments/", headers=_auth(outsider_token))
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_deployments_admin_sees_everything(client):
    owner_token = _register_and_login(client, "alice")
    _deploy(client, owner_token, lab_template_id=_any_lab_template_id(client, owner_token))

    admin_token = _admin_token(client)
    resp = client.get("/api/v1/deployments/", headers=_auth(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ── destroy / visibility-change / reset ─────────────────────────────────────

def test_owner_can_destroy_own_running_deployment(client, db_session):
    token = _register_and_login(client, "alice")
    body = _deploy(client, token, lab_template_id=_any_lab_template_id(client, token))
    _force_running(db_session, body["id"])

    resp = client.delete(f"/api/v1/deployments/{body['id']}", headers=_auth(token))
    assert resp.status_code == 202


def test_unrelated_user_cannot_destroy_deployment(client, db_session):
    owner_token = _register_and_login(client, "alice")
    body = _deploy(client, owner_token, lab_template_id=_any_lab_template_id(client, owner_token))
    _force_running(db_session, body["id"])

    outsider_token = _register_and_login(client, "bob")
    resp = client.delete(f"/api/v1/deployments/{body['id']}", headers=_auth(outsider_token))
    assert resp.status_code == 404


def test_team_manager_can_destroy_member_deployment(client, db_session):
    owner_token = _register_and_login(client, "alice")
    team = client.post("/api/v1/teams/", json={"name": "Red Team"}, headers=_auth(owner_token)).json()

    member_token = _register_and_login(client, "bob")
    invite = client.post(
        f"/api/v1/teams/{team['id']}/invite",
        json={"username": "bob", "role": "manager"},
        headers=_auth(owner_token),
    ).json()
    client.post(f"/api/v1/invitations/{invite['token']}/accept", headers=_auth(member_token))

    carol_token = _register_and_login(client, "carol")
    invite2 = client.post(
        f"/api/v1/teams/{team['id']}/invite",
        json={"username": "carol", "role": "member"},
        headers=_auth(owner_token),
    ).json()
    client.post(f"/api/v1/invitations/{invite2['token']}/accept", headers=_auth(carol_token))

    template_id = _any_lab_template_id(client, carol_token)
    body = _deploy(client, carol_token, lab_template_id=template_id, team_id=team["id"])
    _force_running(db_session, body["id"])

    resp = client.delete(f"/api/v1/deployments/{body['id']}", headers=_auth(member_token))
    assert resp.status_code == 202


def test_cannot_destroy_deployment_that_is_still_starting(client):
    token = _register_and_login(client, "alice")
    body = _deploy(client, token, lab_template_id=_any_lab_template_id(client, token))

    resp = client.delete(f"/api/v1/deployments/{body['id']}", headers=_auth(token))
    assert resp.status_code == 400


def test_owner_can_change_visibility(client):
    token = _register_and_login(client, "alice")
    body = _deploy(client, token, lab_template_id=_any_lab_template_id(client, token))

    resp = client.patch(
        f"/api/v1/deployments/{body['id']}/visibility",
        params={"visibility": "public"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["visibility"] == "public"


def test_unrelated_user_cannot_change_visibility(client):
    owner_token = _register_and_login(client, "alice")
    body = _deploy(client, owner_token, lab_template_id=_any_lab_template_id(client, owner_token))

    outsider_token = _register_and_login(client, "bob")
    resp = client.patch(
        f"/api/v1/deployments/{body['id']}/visibility",
        params={"visibility": "public"},
        headers=_auth(outsider_token),
    )
    assert resp.status_code == 404


def test_reset_rejected_for_non_firerange_lab(client, db_session):
    token = _register_and_login(client, "alice")
    labs = client.get("/api/v1/labs/", headers=_auth(token)).json()
    non_firerange = next(l for l in labs if l["category"] != "firerange")

    body = _deploy(client, token, lab_template_id=non_firerange["id"])
    _force_running(db_session, body["id"])

    resp = client.post(f"/api/v1/deployments/{body['id']}/reset", headers=_auth(token))
    assert resp.status_code == 400


def test_reset_allowed_for_firerange_lab_owner(client, db_session):
    token = _register_and_login(client, "alice")
    template_id = _firerange_lab_template_id(client, token)

    body = _deploy(client, token, lab_template_id=template_id)
    _force_running(db_session, body["id"])

    resp = client.post(f"/api/v1/deployments/{body['id']}/reset", headers=_auth(token))
    assert resp.status_code == 202


def test_unrelated_user_cannot_reset_deployment(client, db_session):
    owner_token = _register_and_login(client, "alice")
    template_id = _firerange_lab_template_id(client, owner_token)
    body = _deploy(client, owner_token, lab_template_id=template_id)
    _force_running(db_session, body["id"])

    outsider_token = _register_and_login(client, "bob")
    resp = client.post(f"/api/v1/deployments/{body['id']}/reset", headers=_auth(outsider_token))
    assert resp.status_code == 404


# ── per-deployment network isolation / concurrency ──────────────────────────

def test_deployment_gets_a_subnet_and_per_deployment_container_names(client):
    token = _register_and_login(client, "alice")
    template_id = _any_lab_template_id(client, token)
    body = _deploy(client, token, lab_template_id=template_id)

    assert body["subnet"]
    assert body["app_ip"]
    assert body["network_name"]
    assert all(str(body["id"]) in name for name in body["container_names"])


def test_different_users_can_run_the_same_lab_concurrently(client):
    alice_token = _register_and_login(client, "alice")
    template_id = _any_lab_template_id(client, alice_token)
    alice_dep = _deploy(client, alice_token, lab_template_id=template_id)

    bob_token = _register_and_login(client, "bob")
    bob_dep = _deploy(client, bob_token, lab_template_id=template_id)

    assert alice_dep["subnet"] != bob_dep["subnet"]
    assert alice_dep["container_names"] != bob_dep["container_names"]


def test_same_user_double_starting_same_lab_is_rejected(client):
    token = _register_and_login(client, "alice")
    template_id = _any_lab_template_id(client, token)
    _deploy(client, token, lab_template_id=template_id)

    resp = client.post(
        "/api/v1/deployments/", json={"lab_template_id": template_id}, headers=_auth(token)
    )
    assert resp.status_code == 409


def test_different_teams_can_run_the_same_lab_concurrently(client):
    alice_token = _register_and_login(client, "alice")
    red_team = client.post("/api/v1/teams/", json={"name": "Red Team"}, headers=_auth(alice_token)).json()
    template_id = _any_lab_template_id(client, alice_token)
    red_dep = _deploy(client, alice_token, lab_template_id=template_id, team_id=red_team["id"])

    bob_token = _register_and_login(client, "bob")
    blue_team = client.post("/api/v1/teams/", json={"name": "Blue Team"}, headers=_auth(bob_token)).json()
    blue_dep = _deploy(client, bob_token, lab_template_id=template_id, team_id=blue_team["id"])

    assert red_dep["subnet"] != blue_dep["subnet"]


def test_same_team_double_starting_same_lab_is_rejected(client):
    token = _register_and_login(client, "alice")
    team = client.post("/api/v1/teams/", json={"name": "Red Team"}, headers=_auth(token)).json()
    template_id = _any_lab_template_id(client, token)
    _deploy(client, token, lab_template_id=template_id, team_id=team["id"])

    resp = client.post(
        "/api/v1/deployments/",
        json={"lab_template_id": template_id, "team_id": team["id"]},
        headers=_auth(token),
    )
    assert resp.status_code == 409
