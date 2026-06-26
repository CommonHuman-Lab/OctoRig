# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Tests for /api/v1/profiles/* — privacy levels gating profile visibility,
the activity feed toggle, and user search excluding the caller. No real
DB, no real network — see tests/conftest.py.
"""
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


# ── access control ───────────────────────────────────────────────────────────

def test_profiles_require_authentication(client):
    assert client.get("/api/v1/profiles/me").status_code == 401
    assert client.get("/api/v1/profiles/alice").status_code == 401


# ── own profile ──────────────────────────────────────────────────────────────

def test_get_my_profile_creates_sane_defaults(client):
    token = _register_and_login(client, "alice")
    resp = client.get("/api/v1/profiles/me", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "alice"
    assert body["privacy_level"] == "public"
    assert body["total_points"] == 0


def test_update_my_profile_partial(client):
    token = _register_and_login(client, "alice")
    resp = client.patch(
        "/api/v1/profiles/me",
        json={"bio": "Hello world", "github_handle": "alice-h4x"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["bio"] == "Hello world"
    assert body["github_handle"] == "alice-h4x"


def test_update_privacy_level(client):
    token = _register_and_login(client, "alice")
    resp = client.patch(
        "/api/v1/profiles/me", json={"privacy_level": "private"}, headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["privacy_level"] == "private"


# ── viewing other users' profiles ───────────────────────────────────────────

def test_public_profile_visible_to_other_users(client):
    _register_and_login(client, "alice")
    bob_token = _register_and_login(client, "bob")

    resp = client.get("/api/v1/profiles/alice", headers=_auth(bob_token))
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"


def test_private_profile_hidden_from_other_users(client):
    alice_token = _register_and_login(client, "alice")
    client.patch("/api/v1/profiles/me", json={"privacy_level": "private"}, headers=_auth(alice_token))

    bob_token = _register_and_login(client, "bob")
    resp = client.get("/api/v1/profiles/alice", headers=_auth(bob_token))
    assert resp.status_code == 404


def test_private_profile_still_visible_to_owner(client):
    alice_token = _register_and_login(client, "alice")
    client.patch("/api/v1/profiles/me", json={"privacy_level": "private"}, headers=_auth(alice_token))

    resp = client.get("/api/v1/profiles/alice", headers=_auth(alice_token))
    assert resp.status_code == 200


def test_unknown_username_404(client):
    token = _register_and_login(client, "alice")
    resp = client.get("/api/v1/profiles/no-such-user", headers=_auth(token))
    assert resp.status_code == 404


def test_inactive_user_profile_hidden(client):
    admin_token = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "Unit-Test-Admin-Pw-9000!"}
    ).json()["access_token"]
    alice_token = _register_and_login(client, "alice")
    bob_token = _register_and_login(client, "bob")
    bob_id = client.get("/api/v1/auth/me", headers=_auth(bob_token)).json()["id"]

    client.patch(f"/api/v1/admin/users/{bob_id}", json={"is_active": False}, headers=_auth(admin_token))

    resp = client.get("/api/v1/profiles/bob", headers=_auth(alice_token))
    assert resp.status_code == 404


# ── activity feed toggle ─────────────────────────────────────────────────────

def test_recent_solves_hidden_when_show_activity_disabled(client, db_session):
    from app.models.challenge import (
        Challenge,
        ChallengeDifficulty,
        ChallengeFlag,
        ChallengeType,
        FlagType,
    )

    ch = Challenge(
        slug="activity-test", title="Activity Test", description="x",
        challenge_type=ChallengeType.FLAG, difficulty=ChallengeDifficulty.EASY,
        category="web", points=50,
    )
    db_session.add(ch)
    db_session.flush()
    db_session.add(ChallengeFlag(challenge_id=ch.id, flag_type=FlagType.STATIC, value="FLAG{x}"))
    db_session.commit()

    alice_token = _register_and_login(client, "alice")
    client.post("/api/v1/challenges/activity-test/submit", json={"flag": "FLAG{x}"}, headers=_auth(alice_token))
    client.patch("/api/v1/profiles/me", json={"show_activity": False}, headers=_auth(alice_token))

    bob_token = _register_and_login(client, "bob")
    resp = client.get("/api/v1/profiles/alice", headers=_auth(bob_token))
    assert resp.status_code == 200
    assert resp.json()["recent_solves"] == []
    assert resp.json()["solve_count"] == 1  # aggregate stats still shown


def test_recent_solves_always_visible_to_owner_even_if_hidden(client, db_session):
    from app.models.challenge import (
        Challenge,
        ChallengeDifficulty,
        ChallengeFlag,
        ChallengeType,
        FlagType,
    )

    ch = Challenge(
        slug="activity-test2", title="Activity Test 2", description="x",
        challenge_type=ChallengeType.FLAG, difficulty=ChallengeDifficulty.EASY,
        category="web", points=50,
    )
    db_session.add(ch)
    db_session.flush()
    db_session.add(ChallengeFlag(challenge_id=ch.id, flag_type=FlagType.STATIC, value="FLAG{y}"))
    db_session.commit()

    alice_token = _register_and_login(client, "alice")
    client.post("/api/v1/challenges/activity-test2/submit", json={"flag": "FLAG{y}"}, headers=_auth(alice_token))
    client.patch("/api/v1/profiles/me", json={"show_activity": False}, headers=_auth(alice_token))

    resp = client.get("/api/v1/profiles/me", headers=_auth(alice_token))
    assert len(resp.json()["recent_solves"]) == 1


# ── search ───────────────────────────────────────────────────────────────────

def test_search_excludes_self(client):
    alice_token = _register_and_login(client, "alice")
    _register_and_login(client, "alice2")

    resp = client.get("/api/v1/profiles/search", params={"q": "alice"}, headers=_auth(alice_token))
    assert resp.status_code == 200
    usernames = {u["username"] for u in resp.json()}
    assert usernames == {"alice2"}


def test_search_excludes_inactive_users(client):
    admin_token = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "Unit-Test-Admin-Pw-9000!"}
    ).json()["access_token"]
    alice_token = _register_and_login(client, "alice")
    bob_token = _register_and_login(client, "bob")
    bob_id = client.get("/api/v1/auth/me", headers=_auth(bob_token)).json()["id"]

    client.patch(f"/api/v1/admin/users/{bob_id}", json={"is_active": False}, headers=_auth(admin_token))

    resp = client.get("/api/v1/profiles/search", params={"q": "bob"}, headers=_auth(alice_token))
    assert resp.status_code == 200
    assert resp.json() == []
