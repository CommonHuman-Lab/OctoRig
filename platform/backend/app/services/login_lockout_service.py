# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Account-level login lockout — brute-force protection independent of source IP.

The /auth/login endpoint is also rate-limited per-IP (see app/core/limiter.py),
but that alone does not stop credential-stuffing against a single account from
many different IPs. This tracks failed attempts per-account and locks it out
with exponential backoff, regardless of where the requests come from.
"""

from datetime import UTC, datetime, timedelta

from app.core.db_types import ensure_aware
from app.models.user import User

THRESHOLD = 5  # failed attempts before a lockout is applied
BASE_LOCKOUT_MINUTES = 15
MAX_LOCKOUT_MINUTES = 240  # 4 hours


def is_locked(user: User) -> bool:
    locked_until = ensure_aware(user.locked_until)
    return locked_until is not None and locked_until > datetime.now(UTC)


def record_failed_attempt(user: User) -> None:
    """Increment the failure counter and apply/extend a lockout every `THRESHOLD` failures."""
    user.failed_login_attempts += 1
    if user.failed_login_attempts % THRESHOLD == 0:
        lockout_count = user.failed_login_attempts // THRESHOLD
        minutes = min(BASE_LOCKOUT_MINUTES * (2 ** (lockout_count - 1)), MAX_LOCKOUT_MINUTES)
        user.locked_until = datetime.now(UTC) + timedelta(minutes=minutes)


def reset(user: User) -> None:
    user.failed_login_attempts = 0
    user.locked_until = None
