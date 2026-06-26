# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Two candidates assigned the same lab must get isolated, non-colliding
network allocations — this is the bug that motivated per-deployment network
isolation (assessments.start_assessment never went through the ad-hoc
deployment conflict check, so concurrent candidates used to force-kill each
other's containers). Docker is mocked by the autouse `no_docker` fixture in
conftest.py.
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


def _any_world_lab_slug(client, admin_token):
    labs = client.get(
        "/api/v1/labs/", params={"category": "world"}, headers=_auth(admin_token)
    ).json()
    assert labs, "no world lab templates were seeded at startup"
    return labs[0]["slug"]


def _create_assessment(client, admin_token, lab_slugs):
    resp = client.post(
        "/api/v1/admin/assessments/",
        json={"name": "Round-1", "lab_slugs": lab_slugs},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _invite_and_accept(client, admin_token, assessment_id, email, username):
    invite = client.post(
        f"/api/v1/admin/assessments/{assessment_id}/invites",
        json={"email": email, "candidate_name": username},
        headers=_auth(admin_token),
    ).json()

    resp = client.post(
        f"/api/v1/assessments/invite/{invite['token']}/accept",
        json={"username": username, "password": PASSWORD},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def test_two_candidates_on_the_same_lab_get_isolated_deployments(client, db_session):
    from app.models.assessment import AssessmentInvite

    admin_token = _admin_token(client)
    lab_slug = _any_world_lab_slug(client, admin_token)
    assessment = _create_assessment(client, admin_token, [lab_slug])

    moe_token = _invite_and_accept(client, admin_token, assessment["id"], "moe@example.com", "moe")
    larry_token = _invite_and_accept(
        client, admin_token, assessment["id"], "larry@example.com", "larry"
    )

    moe_resp = client.post("/api/v1/assessments/me/start", headers=_auth(moe_token))
    assert moe_resp.status_code == 200, moe_resp.text
    larry_resp = client.post("/api/v1/assessments/me/start", headers=_auth(larry_token))
    assert larry_resp.status_code == 200, larry_resp.text

    moe_invite = db_session.query(AssessmentInvite).filter_by(candidate_name="moe").first()
    larry_invite = db_session.query(AssessmentInvite).filter_by(candidate_name="larry").first()

    from app.models.deployment import Deployment

    moe_dep = db_session.get(Deployment, moe_invite.deployment_ids[0])
    larry_dep = db_session.get(Deployment, larry_invite.deployment_ids[0])

    assert moe_dep.subnet is not None
    assert larry_dep.subnet is not None
    assert moe_dep.subnet != larry_dep.subnet
    assert moe_dep.network_name != larry_dep.network_name
    assert moe_dep.container_names != larry_dep.container_names
