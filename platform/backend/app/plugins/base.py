# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from collections.abc import Callable
from typing import Literal, Protocol, runtime_checkable

from fastapi import FastAPI


@runtime_checkable
class OctoPlugin(Protocol):
    """Interface every OctoRig plugin must satisfy."""

    name: str
    version: str
    plugin_type: Literal["challenge_type", "scoring_engine", "auth_provider", "lab_provider"]

    def register(self, app: FastAPI, db_session_factory: Callable) -> None:
        """Mount additional routes or startup logic into the platform app."""
        ...
