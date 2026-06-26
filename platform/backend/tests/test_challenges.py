# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Tests for /api/v1/challenges/* — flag submission, hint unlocking, scoring,
and admin-only management. Flag-submission rate limiting talks to Redis in
production; the autouse `no_redis` fixture in conftest.py swaps it for an
in-memory fake, so these tests never touch a real Redis instance. No real
DB, no real network, no real Docker, no real Redis — see tests/conftest.py.
"""

import os

from app.models.challenge import (
    Challenge,
    ChallengeDifficulty,
    ChallengeFlag,
    ChallengeHint,
    ChallengeType,
    FlagType,
)

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


def _make_challenge(db_session, slug="test-chal", points=100, flag="FLAG{test}", hint_cost=0):
    ch = Challenge(
        slug=slug,
        title="Test Challenge",
        description="A challenge for tests",
        challenge_type=ChallengeType.FLAG,
        difficulty=ChallengeDifficulty.EASY,
        category="web",
        points=points,
    )
    db_session.add(ch)
    db_session.flush()

    db_session.add(ChallengeFlag(challenge_id=ch.id, flag_type=FlagType.STATIC, value=flag))
    db_session.add(ChallengeHint(challenge_id=ch.id, order_num=1, content="psst", cost=hint_cost))
    db_session.commit()
    db_session.refresh(ch)
    return ch


# ── listing / detail ─────────────────────────────────────────────────────────


def test_list_challenges_requires_authentication(client):
    resp = client.get("/api/v1/challenges/")
    assert resp.status_code == 401


def test_list_challenges_includes_seeded_test_challenge(client, db_session):
    _make_challenge(db_session)
    token = _register_and_login(client, "alice")

    resp = client.get("/api/v1/challenges/", headers=_auth(token))
    assert resp.status_code == 200
    assert "test-chal" in {c["slug"] for c in resp.json()}


def test_get_challenge_detail_hides_locked_hint_content(client, db_session):
    _make_challenge(db_session, hint_cost=10)
    token = _register_and_login(client, "alice")

    resp = client.get("/api/v1/challenges/test-chal", headers=_auth(token))
    assert resp.status_code == 200
    hint = resp.json()["hints"][0]
    assert hint["unlocked"] is False
    assert hint["content"] is None


def test_get_unknown_challenge_404(client):
    token = _register_and_login(client, "alice")
    resp = client.get("/api/v1/challenges/no-such-challenge", headers=_auth(token))
    assert resp.status_code == 404


# ── flag submission ──────────────────────────────────────────────────────────


def test_correct_flag_awards_points(client, db_session):
    _make_challenge(db_session, points=150, flag="FLAG{correct}")
    token = _register_and_login(client, "alice")

    resp = client.post(
        "/api/v1/challenges/test-chal/submit", json={"flag": "FLAG{correct}"}, headers=_auth(token)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["correct"] is True
    assert body["points_awarded"] == 150
    assert body["first_blood"] is True


def test_incorrect_flag_rejected_without_points(client, db_session):
    _make_challenge(db_session, flag="FLAG{correct}")
    token = _register_and_login(client, "alice")

    resp = client.post(
        "/api/v1/challenges/test-chal/submit", json={"flag": "FLAG{wrong}"}, headers=_auth(token)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["correct"] is False
    assert body["points_awarded"] == 0


def test_resubmitting_after_solve_reports_already_solved(client, db_session):
    _make_challenge(db_session, flag="FLAG{correct}")
    token = _register_and_login(client, "alice")

    client.post(
        "/api/v1/challenges/test-chal/submit", json={"flag": "FLAG{correct}"}, headers=_auth(token)
    )
    second = client.post(
        "/api/v1/challenges/test-chal/submit", json={"flag": "FLAG{correct}"}, headers=_auth(token)
    )
    assert second.status_code == 200
    body = second.json()
    assert body["already_solved"] is True
    assert body["points_awarded"] == 0


def test_second_solver_does_not_get_first_blood(client, db_session):
    _make_challenge(db_session, flag="FLAG{correct}")
    alice_token = _register_and_login(client, "alice")
    bob_token = _register_and_login(client, "bob")

    client.post(
        "/api/v1/challenges/test-chal/submit",
        json={"flag": "FLAG{correct}"},
        headers=_auth(alice_token),
    )
    resp = client.post(
        "/api/v1/challenges/test-chal/submit",
        json={"flag": "FLAG{correct}"},
        headers=_auth(bob_token),
    )
    assert resp.status_code == 200
    assert resp.json()["first_blood"] is False


def test_flag_submission_never_touches_real_redis(client, db_session):
    """Asserts the autouse no_redis mock is actually wired in for both the
    rate limiter (app.api.challenges) and the scoreboard cache
    (app.services.scoring_service) — if this starts failing, submissions may
    be hitting a real Redis instance instead of the in-memory fake."""
    import redis as redis_lib

    import app.api.challenges as challenges_module
    import app.services.scoring_service as scoring_service

    assert not isinstance(challenges_module._get_redis(), redis_lib.Redis)
    assert not isinstance(scoring_service._get_redis(), redis_lib.Redis)

    _make_challenge(db_session, flag="FLAG{correct}")
    token = _register_and_login(client, "alice")
    resp = client.post(
        "/api/v1/challenges/test-chal/submit", json={"flag": "FLAG{correct}"}, headers=_auth(token)
    )
    assert resp.status_code == 200


def test_max_flag_attempts_enforced_when_configured(client, db_session):
    _make_challenge(db_session, flag="FLAG{correct}")
    admin_token = _admin_token(client)
    client.patch(
        "/api/v1/admin/settings", json={"max_flag_attempts": 2}, headers=_auth(admin_token)
    )

    token = _register_and_login(client, "alice")
    client.post(
        "/api/v1/challenges/test-chal/submit", json={"flag": "wrong1"}, headers=_auth(token)
    )
    client.post(
        "/api/v1/challenges/test-chal/submit", json={"flag": "wrong2"}, headers=_auth(token)
    )

    third = client.post(
        "/api/v1/challenges/test-chal/submit", json={"flag": "wrong3"}, headers=_auth(token)
    )
    assert third.status_code == 429


# ── hints ────────────────────────────────────────────────────────────────────


def test_unlock_free_hint(client, db_session):
    _make_challenge(db_session, hint_cost=0)
    token = _register_and_login(client, "alice")
    ch = db_session.query(Challenge).filter_by(slug="test-chal").first()
    hint_id = db_session.query(ChallengeHint).filter_by(challenge_id=ch.id).first().id

    resp = client.post(f"/api/v1/challenges/test-chal/hints/{hint_id}/unlock", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["content"] == "psst"


def test_unlock_hint_insufficient_points_rejected(client, db_session):
    _make_challenge(db_session, hint_cost=999999)
    token = _register_and_login(client, "alice")
    ch = db_session.query(Challenge).filter_by(slug="test-chal").first()
    hint_id = db_session.query(ChallengeHint).filter_by(challenge_id=ch.id).first().id

    resp = client.post(f"/api/v1/challenges/test-chal/hints/{hint_id}/unlock", headers=_auth(token))
    assert resp.status_code == 400


def test_unlock_hint_deducts_points(client, db_session):
    _make_challenge(db_session, points=200, flag="FLAG{correct}", hint_cost=20)
    token = _register_and_login(client, "alice")

    client.post(
        "/api/v1/challenges/test-chal/submit", json={"flag": "FLAG{correct}"}, headers=_auth(token)
    )

    ch = db_session.query(Challenge).filter_by(slug="test-chal").first()
    hint_id = db_session.query(ChallengeHint).filter_by(challenge_id=ch.id).first().id
    client.post(f"/api/v1/challenges/test-chal/hints/{hint_id}/unlock", headers=_auth(token))

    me = client.get("/api/v1/auth/me", headers=_auth(token)).json()
    score_resp = client.get(f"/api/v1/scoreboards/users/{me['id']}", headers=_auth(token))
    assert score_resp.status_code == 200
    assert score_resp.json()["total"] == 180


# ── admin-only management ───────────────────────────────────────────────────


def test_admin_list_all_requires_admin(client, db_session):
    _make_challenge(db_session)
    player_token = _register_and_login(client, "alice")
    resp = client.get("/api/v1/challenges/admin/all", headers=_auth(player_token))
    assert resp.status_code == 403


def test_admin_can_deactivate_challenge(client, db_session):
    _make_challenge(db_session)
    admin_token = _admin_token(client)

    resp = client.patch(
        "/api/v1/challenges/test-chal/active", json={"is_active": False}, headers=_auth(admin_token)
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_player_cannot_deactivate_challenge(client, db_session):
    _make_challenge(db_session)
    player_token = _register_and_login(client, "alice")

    resp = client.patch(
        "/api/v1/challenges/test-chal/active",
        json={"is_active": False},
        headers=_auth(player_token),
    )
    assert resp.status_code == 403
