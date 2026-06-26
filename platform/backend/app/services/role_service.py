# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from sqlalchemy.orm import Session

from app.core.permissions import (
    ALL_ADMIN_PERMS,
    ALL_PLATFORM_PERMS,
    PERM_ADMIN_CHALLENGES_MANAGE,
    PERM_ADMIN_EVENTS_MANAGE,
    PERM_ADMIN_PANEL,
    PERM_CREATOR_ACCESS,
    PERM_PLATFORM_BADGES,
    PERM_PLATFORM_DASHBOARD,
    PERM_PLATFORM_SCOREBOARD,
)
from app.models.role import PlatformRole

ROLE_SEED = [
    {
        "slug": "admin",
        "display_name": "Admin",
        "description": "Full administrative access to everything.",
        "permissions": ALL_PLATFORM_PERMS + ALL_ADMIN_PERMS + [PERM_CREATOR_ACCESS],
        "is_system": True,
        "is_default": False,
    },
    {
        "slug": "creator",
        "display_name": "Creator",
        "description": "Platform access plus challenge/event creation.",
        "permissions": ALL_PLATFORM_PERMS
        + [
            PERM_CREATOR_ACCESS,
            PERM_ADMIN_PANEL,
            PERM_ADMIN_CHALLENGES_MANAGE,
            PERM_ADMIN_EVENTS_MANAGE,
        ],
        "is_system": True,
        "is_default": False,
    },
    {
        "slug": "player",
        "display_name": "Player",
        "description": "Default role for new users — full access to platform pages.",
        "permissions": list(ALL_PLATFORM_PERMS),
        "is_system": True,
        "is_default": True,
    },
    {
        "slug": "viewer",
        "display_name": "Viewer",
        "description": "Read-only access to public platform pages.",
        "permissions": [PERM_PLATFORM_DASHBOARD, PERM_PLATFORM_SCOREBOARD, PERM_PLATFORM_BADGES],
        "is_system": True,
        "is_default": False,
    },
]


def seed_roles(db: Session) -> int:
    """Upsert system roles. Safe to call on every startup.

    System roles have their permissions/display_name refreshed each time so
    that new permission keys added in code propagate without a data
    migration. Custom (non-system) roles created by admins are left alone.
    """
    inserted = 0
    for entry in ROLE_SEED:
        existing = db.query(PlatformRole).filter(PlatformRole.slug == entry["slug"]).first()
        if existing is None:
            db.add(PlatformRole(**entry))
            inserted += 1
        elif existing.is_system:
            existing.permissions = entry["permissions"]
            existing.display_name = entry["display_name"]
            existing.description = entry["description"]
            existing.is_default = entry["is_default"]
    db.commit()
    return inserted
