# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Structured JSON logging configuration.

Call configure_logging() once at process startup (main.py, celery_app.py).
All subsequent logging.getLogger(...).info(...) calls emit JSON lines with
consistent fields: timestamp, level, logger, message, plus any extra kwargs.
"""

import logging
import sys

from pythonjsonlogger import jsonlogger


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
            rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        )
    )

    root = logging.getLogger()
    root.setLevel(level)
    # Replace any existing handlers (e.g. uvicorn's default plain-text handler)
    root.handlers.clear()
    root.addHandler(handler)

    # Quieten overly noisy libraries
    logging.getLogger("docker").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
