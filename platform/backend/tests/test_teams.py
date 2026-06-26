# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Tests for /api/v1/teams/* — team CRUD, membership, invitations, and the
role-hierarchy authorization boundaries (viewer < member < manager < owner),
including the platform-admin bypass. No real DB, no real network — see
tests/conftest.py.
"""

import os

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
PASSWORD = "StrongPassw0rd!"


def _register_and_login(client, username):
    email = f"{username}@example.com"
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": PASSWORD},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _admin_token(client):
    return client.post(
        "/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    ).json()["access_token"]


def _create_team(client, token, name="Red Team"):
    resp = client.post("/api/v1/teams/", json={"name": name}, headers=_auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


def _invite(client, owner_token, team_id, username, role="member"):
    return client.post(
        f"/api/v1/teams/{team_id}/invite",
        json={"username": username, "role": role},
        headers=_auth(owner_token),
    )


def _accept(client, member_token, invitation_token):
    return client.post(
        f"/api/v1/invitations/{invitation_token}/accept", headers=_auth(member_token)
    )


def _add_member(client, owner_token, member_token, team_id, username, role="member"):
    """Invite + accept in one step, returns the membership response."""
    inv = _invite(client, owner_token, team_id, username, role=role)
    assert inv.status_code == 201, inv.text
    accept = _accept(client, member_token, inv.json()["token"])
    assert accept.status_code == 201, accept.text
    return accept.json()


# ── create / list ────────────────────────────────────────────────────────────


def test_create_team_makes_caller_owner(client):
    token = _register_and_login(client, "alice")
    team = _create_team(client, token)
    assert team["my_role"] == "owner"
    assert team["member_count"] == 1
    assert team["is_personal"] is False


def test_create_team_rejects_duplicate_name(client):
    token = _register_and_login(client, "alice")
    _create_team(client, token, name="Red Team")
    resp = client.post("/api/v1/teams/", json={"name": "Red Team"}, headers=_auth(token))
    assert resp.status_code == 409


def test_create_team_rejects_blank_name(client):
    token = _register_and_login(client, "alice")
    resp = client.post("/api/v1/teams/", json={"name": "   "}, headers=_auth(token))
    assert resp.status_code == 422


def test_list_teams_includes_personal_and_created_teams(client):
    token = _register_and_login(client, "alice")
    _create_team(client, token, name="Red Team")
    resp = client.get("/api/v1/teams/", headers=_auth(token))
    assert resp.status_code == 200
    names = {t["name"] for t in resp.json()}
    assert "Red Team" in names
    assert any(t["is_personal"] for t in resp.json())


# ── get / membership visibility ─────────────────────────────────────────────


def test_get_team_denied_for_non_member(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)

    outsider_token = _register_and_login(client, "bob")
    resp = client.get(f"/api/v1/teams/{team['id']}", headers=_auth(outsider_token))
    assert resp.status_code == 404


def test_get_team_allowed_for_platform_admin_without_membership(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)

    admin_token = _admin_token(client)
    resp = client.get(f"/api/v1/teams/{team['id']}", headers=_auth(admin_token))
    assert resp.status_code == 200


def test_list_members_denied_for_non_member(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)

    outsider_token = _register_and_login(client, "bob")
    resp = client.get(f"/api/v1/teams/{team['id']}/members", headers=_auth(outsider_token))
    assert resp.status_code == 404


# ── update / delete (manager+/owner boundary) ───────────────────────────────


def test_update_team_requires_manager_or_above(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    member_token = _register_and_login(client, "bob")
    _add_member(client, owner_token, member_token, team["id"], "bob", role="member")

    denied = client.patch(
        f"/api/v1/teams/{team['id']}", json={"name": "Renamed"}, headers=_auth(member_token)
    )
    assert denied.status_code == 403

    allowed = client.patch(
        f"/api/v1/teams/{team['id']}", json={"name": "Renamed"}, headers=_auth(owner_token)
    )
    assert allowed.status_code == 200
    assert allowed.json()["name"] == "Renamed"


def test_delete_team_requires_owner_not_manager(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    manager_token = _register_and_login(client, "bob")
    _add_member(client, owner_token, manager_token, team["id"], "bob", role="manager")

    denied = client.delete(f"/api/v1/teams/{team['id']}", headers=_auth(manager_token))
    assert denied.status_code == 403

    allowed = client.delete(f"/api/v1/teams/{team['id']}", headers=_auth(owner_token))
    assert allowed.status_code == 204


def test_cannot_delete_personal_team(client):
    token = _register_and_login(client, "alice")
    teams = client.get("/api/v1/teams/", headers=_auth(token)).json()
    personal = next(t for t in teams if t["is_personal"])

    resp = client.delete(f"/api/v1/teams/{personal['id']}", headers=_auth(token))
    assert resp.status_code == 400


# ── invitations ──────────────────────────────────────────────────────────────


def test_member_cannot_invite_others(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    member_token = _register_and_login(client, "bob")
    _add_member(client, owner_token, member_token, team["id"], "bob", role="member")

    _register_and_login(client, "carol")
    resp = _invite(client, member_token, team["id"], "carol")
    assert resp.status_code == 403


def test_invite_nonexistent_username_returns_404(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    resp = _invite(client, owner_token, team["id"], "ghost")
    assert resp.status_code == 404


def test_invite_already_member_returns_409(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    member_token = _register_and_login(client, "bob")
    _add_member(client, owner_token, member_token, team["id"], "bob")

    resp = _invite(client, owner_token, team["id"], "bob")
    assert resp.status_code == 409


def test_accept_invitation_grants_membership_with_invited_role(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    member_token = _register_and_login(client, "bob")

    membership = _add_member(client, owner_token, member_token, team["id"], "bob", role="manager")
    assert membership["role"] == "manager"
    assert membership["username"] == "bob"


def test_get_invitation_is_public_and_hides_no_sensitive_data(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    _register_and_login(client, "bob")

    inv = _invite(client, owner_token, team["id"], "bob").json()
    resp = client.get(f"/api/v1/invitations/{inv['token']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["team_name"] == team["name"]
    assert body["invited_by_username"] == "alice"


def test_decline_invitation_prevents_later_acceptance(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    member_token = _register_and_login(client, "bob")

    inv = _invite(client, owner_token, team["id"], "bob").json()
    decline = client.post(
        f"/api/v1/invitations/{inv['token']}/decline", headers=_auth(member_token)
    )
    assert decline.status_code == 204

    accept = _accept(client, member_token, inv["token"])
    assert accept.status_code == 404


# ── remove member / change role / transfer ownership ───────────────────────


def test_member_can_remove_self_without_manager_role(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    member_token = _register_and_login(client, "bob")
    membership = _add_member(client, owner_token, member_token, team["id"], "bob")

    resp = client.delete(
        f"/api/v1/teams/{team['id']}/members/{membership['user_id']}",
        headers=_auth(member_token),
    )
    assert resp.status_code == 204


def test_member_cannot_remove_other_members(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    bob_token = _register_and_login(client, "bob")
    bob = _add_member(client, owner_token, bob_token, team["id"], "bob")
    carol_token = _register_and_login(client, "carol")
    _add_member(client, owner_token, carol_token, team["id"], "carol")

    resp = client.delete(
        f"/api/v1/teams/{team['id']}/members/{bob['user_id']}", headers=_auth(carol_token)
    )
    assert resp.status_code == 403


def test_cannot_remove_last_owner(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    me = client.get("/api/v1/auth/me", headers=_auth(owner_token)).json()

    resp = client.delete(
        f"/api/v1/teams/{team['id']}/members/{me['id']}", headers=_auth(owner_token)
    )
    assert resp.status_code == 400


def test_member_cannot_change_roles(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    bob_token = _register_and_login(client, "bob")
    bob = _add_member(client, owner_token, bob_token, team["id"], "bob")
    carol_token = _register_and_login(client, "carol")
    _add_member(client, owner_token, carol_token, team["id"], "carol")

    resp = client.patch(
        f"/api/v1/teams/{team['id']}/members/{bob['user_id']}",
        json={"role": "manager"},
        headers=_auth(carol_token),
    )
    assert resp.status_code == 403


def test_owner_can_promote_member_to_manager(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    bob_token = _register_and_login(client, "bob")
    bob = _add_member(client, owner_token, bob_token, team["id"], "bob")

    resp = client.patch(
        f"/api/v1/teams/{team['id']}/members/{bob['user_id']}",
        json={"role": "manager"},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "manager"


def test_cannot_demote_last_owner(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    me = client.get("/api/v1/auth/me", headers=_auth(owner_token)).json()

    resp = client.patch(
        f"/api/v1/teams/{team['id']}/members/{me['id']}",
        json={"role": "member"},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 400


def test_manager_cannot_transfer_ownership(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    manager_token = _register_and_login(client, "bob")
    bob = _add_member(client, owner_token, manager_token, team["id"], "bob", role="manager")

    resp = client.post(
        f"/api/v1/teams/{team['id']}/transfer",
        json={"new_owner_id": bob["user_id"]},
        headers=_auth(manager_token),
    )
    assert resp.status_code == 403


def test_owner_can_transfer_ownership_and_is_demoted_to_manager(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    bob_token = _register_and_login(client, "bob")
    bob = _add_member(client, owner_token, bob_token, team["id"], "bob")
    alice = client.get("/api/v1/auth/me", headers=_auth(owner_token)).json()

    resp = client.post(
        f"/api/v1/teams/{team['id']}/transfer",
        json={"new_owner_id": bob["user_id"]},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 204

    members = client.get(f"/api/v1/teams/{team['id']}/members", headers=_auth(bob_token)).json()
    roles = {m["user_id"]: m["role"] for m in members}
    assert roles[bob["user_id"]] == "owner"
    assert roles[alice["id"]] == "manager"


def test_transfer_ownership_to_non_member_rejected(client):
    owner_token = _register_and_login(client, "alice")
    team = _create_team(client, owner_token)
    outsider_token = _register_and_login(client, "bob")
    outsider = client.get("/api/v1/auth/me", headers=_auth(outsider_token)).json()

    resp = client.post(
        f"/api/v1/teams/{team['id']}/transfer",
        json={"new_owner_id": outsider["id"]},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 400
