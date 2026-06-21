# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from sqlalchemy.orm import Session

from app.core.exceptions import conflict


def raise_if_exists(db: Session, model, detail: str, **filters) -> None:
    if db.query(model).filter_by(**filters).first():
        raise conflict(detail)
