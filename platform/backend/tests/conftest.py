# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Shared fixtures for the OctoRig platform backend test suite.

All tests run against an isolated in-memory SQLite database — no real
Postgres, no real Docker socket, no real network calls, no real Redis.

Environment variables that feed app.config.Settings' strict validators must
be set before ANY `app.*` module is imported, since `Settings()` is
instantiated at import time (app/config.py: `settings = Settings()`).
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "unit-test-secret-key-not-for-production-aaaaaaaa")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_EMAIL", "admin@test.local")
os.environ.setdefault("ADMIN_PASSWORD", "Unit-Test-Admin-Pw-9000!")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("MARKETPLACE_TRUSTED_KEYS", "")


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registers every model on Base.metadata before create_all
from app.core.limiter import limiter
from app.database import Base, SessionLocal


@pytest.fixture()
def client():
    """A TestClient wired to a fresh in-memory SQLite DB for this test only.

    Rate limiting is disabled by default so business-logic assertions aren't
    contaminated by slowapi's in-memory bucket (TestClient requests all share
    one fake IP). Tests that specifically exercise rate limiting should
    re-enable it explicitly — see test_auth.py.
    """
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)

    # Reconfigure in place so modules already holding a reference (e.g. lab_service) pick up the new bind
    SessionLocal.configure(bind=test_engine)

    limiter.reset()
    previously_enabled = limiter.enabled
    limiter.enabled = False

    from app.main import create_app

    application = create_app()

    with TestClient(application) as c:
        yield c

    limiter.enabled = previously_enabled
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture()
def rate_limited_client(client):
    """Same as `client`, but with slowapi rate limiting turned back on."""
    limiter.reset()
    limiter.enabled = True
    yield client
    limiter.enabled = False


@pytest.fixture()
def db_session(client):
    """A raw session bound to the same per-test SQLite DB as `client`, for
    setting up or asserting on state the HTTP API has no direct way to reach
    (e.g. forcing a deployment into RUNNING without a real Docker start)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def no_docker(monkeypatch):
    """Lab start/stop/reset talk to the real Docker socket — never allowed in
    unit tests. FastAPI's TestClient runs BackgroundTasks synchronously within
    the request, so anything that schedules lab_service.start_lab, would
    otherwise reach Docker by the time the response comes back. Applied to
    every test automatically; individual tests can still assert on the call
    via these mock objects if they import them from app.services.lab_service.
    """
    from unittest.mock import MagicMock

    import app.services.lab_service as lab_service
    from app.services.docker_runtime import docker_service

    monkeypatch.setattr(lab_service, "start_lab", MagicMock(name="start_lab"))
    monkeypatch.setattr(lab_service, "stop_lab", MagicMock(name="stop_lab"))
    monkeypatch.setattr(lab_service, "reset_lab", MagicMock(name="reset_lab"))
    monkeypatch.setattr(docker_service, "restart_container", MagicMock(name="restart_container"))


class _FakeRedis:
    """Minimal in-process stand-in for the redis-py calls the app makes:
    INCR/EXPIRE/TTL (flag-submission rate limiting) and GET/SETEX/DELETE
    (scoreboard caching). No network."""

    def __init__(self):
        self._counts: dict[str, int] = {}
        self._expiry: dict[str, float] = {}
        self._values: dict[str, str] = {}

    def incr(self, key: str) -> int:
        self._counts[key] = self._counts.get(key, 0) + 1
        return self._counts[key]

    def expire(self, key: str, seconds: int) -> None:
        self._expiry[key] = seconds

    def ttl(self, key: str) -> int:
        return self._expiry.get(key, 60)

    def get(self, key: str) -> str | None:
        return self._values.get(key)

    def setex(self, key: str, seconds: int, value: str) -> None:
        self._values[key] = value
        self._expiry[key] = seconds

    def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if self._values.pop(key, None) is not None:
                deleted += 1
        return deleted


@pytest.fixture(autouse=True)
def no_redis(monkeypatch):
    """Both the flag-submission rate limiter (app.api.challenges) and the
    scoreboard cache (app.services.scoring_service) open their own real
    redis.from_url() connections — never allowed in unit tests. Both are
    swapped for one shared in-memory fake."""
    import app.api.challenges as challenges
    import app.services.scoring_service as scoring_service

    fake = _FakeRedis()
    monkeypatch.setattr(challenges, "_get_redis", lambda: fake)
    monkeypatch.setattr(scoring_service, "_get_redis", lambda: fake)
