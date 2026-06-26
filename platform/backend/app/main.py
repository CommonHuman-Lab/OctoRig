# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.core.limiter import limiter
from app.core.logging import configure_logging

configure_logging(level="DEBUG" if settings.debug else "INFO")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # API serves no HTML — tightest possible CSP
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.ws.manager import manager

    manager.set_loop(asyncio.get_running_loop())
    # Migrations run in the 'migrate' init container; calling alembic here races in multi-replica deployments
    _seed_admin()
    _seed_roles()
    _seed_badges()
    _seed_ranks()
    _sync_labs()
    _load_plugins(app)
    yield


def _load_plugins(app: FastAPI) -> None:
    from app.database import SessionLocal
    from app.plugins.registry import discover_plugins, mount_plugins

    discover_plugins()
    mount_plugins(app, SessionLocal)


def _seed_badges() -> None:
    from app.database import SessionLocal
    from app.services.achievement_service import seed_badge_catalog

    db = SessionLocal()
    try:
        seed_badge_catalog(db)
    finally:
        db.close()


def _seed_roles() -> None:
    from app.database import SessionLocal
    from app.services.role_service import seed_roles

    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()


def _seed_ranks() -> None:
    from app.database import SessionLocal
    from app.services.rank_service import seed_ranks

    db = SessionLocal()
    try:
        seed_ranks(db)
    finally:
        db.close()


def _sync_labs() -> None:
    from app.database import SessionLocal
    from app.services.lab_service import sync_registry

    db = SessionLocal()
    try:
        sync_registry(db)
    finally:
        db.close()


def _seed_admin() -> None:
    from app.core.security import hash_password
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.team_service import ensure_personal_team

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username=settings.admin_username,
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                is_active=True,
                platform_roles=["admin"],
                is_owner=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            ensure_personal_team(db, admin)
    finally:
        db.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="OctoRig Platform API",
        version="3.0.0",
        description="Offensive security training platform — labs, CTF events, challenges, badges",
        lifespan=lifespan,
        # Disable interactive API docs in production — they expose the full schema
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(SecurityHeadersMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key"],
        max_age=600,
    )

    from app.api.admin import router as admin_router
    from app.api.api_keys import router as api_keys_router
    from app.api.assessments import admin_router as assessments_admin_router
    from app.api.assessments import candidate_router as assessments_candidate_router
    from app.api.auth import router as auth_router
    from app.api.badges import router as badges_router
    from app.api.challenges import router as challenges_router
    from app.api.content import router as content_router
    from app.api.deployments import router as deployments_router
    from app.api.events import router as events_router
    from app.api.events_ws import router as ws_router
    from app.api.labs import router as labs_router
    from app.api.marketplace import router as marketplace_router
    from app.api.notes import router as notes_router
    from app.api.notifications import router as notifications_router
    from app.api.profiles import router as profiles_router
    from app.api.ranks import router as ranks_router
    from app.api.roles import router as roles_router
    from app.api.scheduler import router as scheduler_router
    from app.api.scoreboards import router as scoreboards_router
    from app.api.system import router as system_router
    from app.api.teams import invitations_router
    from app.api.teams import router as teams_router

    app.include_router(ws_router)  # /ws/events (no prefix — raw WS path)
    prefix = "/api/v1"
    app.include_router(auth_router, prefix=prefix)
    app.include_router(labs_router, prefix=prefix)
    app.include_router(deployments_router, prefix=prefix)
    app.include_router(system_router, prefix=prefix)
    app.include_router(teams_router, prefix=prefix)
    app.include_router(invitations_router, prefix=prefix)
    app.include_router(api_keys_router, prefix=prefix)
    app.include_router(scheduler_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)
    app.include_router(roles_router, prefix=prefix)
    app.include_router(challenges_router, prefix=prefix)
    app.include_router(ranks_router, prefix=prefix)
    app.include_router(scoreboards_router, prefix=prefix)
    app.include_router(events_router, prefix=prefix)
    app.include_router(badges_router, prefix=prefix)
    app.include_router(profiles_router, prefix=prefix)
    app.include_router(notes_router, prefix=prefix)
    app.include_router(notifications_router, prefix=prefix)
    app.include_router(content_router, prefix=prefix)
    app.include_router(marketplace_router, prefix=prefix)
    app.include_router(assessments_admin_router, prefix=prefix)
    app.include_router(assessments_candidate_router, prefix=prefix)

    return app


app = create_app()
