# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import importlib.metadata
import logging
from typing import Any

from fastapi import FastAPI

from app.plugins.base import OctoPlugin

logger = logging.getLogger(__name__)

_ENTRY_POINT_GROUP = "octorig.plugins"

_registry: list[dict[str, Any]] = []


def discover_plugins() -> list[dict[str, Any]]:
    """Find all installed plugins via entry_points(group='octorig.plugins')."""
    global _registry
    _registry = []
    eps = importlib.metadata.entry_points(group=_ENTRY_POINT_GROUP)
    for ep in eps:
        try:
            plugin_class = ep.load()
            instance = plugin_class()
            if not isinstance(instance, OctoPlugin):
                logger.warning("Plugin %s does not satisfy OctoPlugin protocol", ep.name)
                continue
            _registry.append(
                {
                    "name": instance.name,
                    "version": instance.version,
                    "plugin_type": instance.plugin_type,
                    "entry_point": ep.name,
                    "_instance": instance,
                }
            )
            logger.info(
                "Discovered plugin: %s v%s (%s)",
                instance.name,
                instance.version,
                instance.plugin_type,
            )
        except Exception:
            logger.exception("Failed to load plugin: %s", ep.name)
    return _registry


def mount_plugins(app: FastAPI, db_session_factory) -> None:
    """Call register() on each discovered plugin."""
    for plugin_meta in _registry:
        instance: OctoPlugin = plugin_meta["_instance"]
        try:
            instance.register(app, db_session_factory)
            logger.info("Mounted plugin: %s", instance.name)
        except Exception:
            logger.exception("Failed to mount plugin: %s", instance.name)


def list_plugins() -> list[dict[str, Any]]:
    return [
        {
            "name": p["name"],
            "version": p["version"],
            "plugin_type": p["plugin_type"],
            "entry_point": p["entry_point"],
        }
        for p in _registry
    ]
