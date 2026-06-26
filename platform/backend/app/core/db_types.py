# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import UTC, datetime

from sqlalchemy import Enum as _SAEnum


def EnumCol(enum_class, **kwargs):
    """SQLAlchemy Enum column that stores .value (not .name) for native Postgres enums."""
    return _SAEnum(
        enum_class,
        values_callable=lambda obj: [e.value for e in obj],
        **kwargs,
    )


def ensure_aware(dt: datetime | None) -> datetime | None:
    """Normalize a DateTime(timezone=True) value to a UTC-aware datetime.

    Postgres reliably round-trips tzinfo for timezone-aware columns, but
    SQLite does not — a value written as UTC comes back naive. Every value
    this column type holds is written as UTC, so a naive read-back is always
    UTC; this makes comparisons against datetime.now(timezone.utc) safe
    regardless of backend.
    """
    if dt is None or dt.tzinfo is not None:
        return dt
    return dt.replace(tzinfo=UTC)
