# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Lab registry — authoritative Python source for all OctoRig labs.

Mirrors the LABS array in octorig.sh but adds the full Docker orchestration
metadata needed by DockerRuntimeService. Each entry is a LabDefinition TypedDict
that maps 1-to-1 to the LabTemplate SQLAlchemy model so sync_registry() can
upsert them directly.

Sub-modules:
  world       — realistic scenario labs (IDs 1–8, 18)
  firerange   — scanner fire-range targets (IDs 9–12)
  thirdparty  — pulled from Docker Hub (IDs 13–17)
  standalone  — standalone challenges with no Docker lab (Python coding challenges)
"""

from ._types import ChallengeDef, FlagDef, HintDef, LabDefinition
from .firerange import FIRERANGE_LABS
from .standalone import STANDALONE_CHALLENGES
from .thirdparty import THIRDPARTY_LABS
from .world import WORLD_LABS

LAB_REGISTRY: list[LabDefinition] = WORLD_LABS + FIRERANGE_LABS + THIRDPARTY_LABS

REGISTRY_BY_SLUG: dict[str, LabDefinition] = {lab["slug"]: lab for lab in LAB_REGISTRY}
REGISTRY_BY_ID: dict[int, LabDefinition] = {lab["id"]: lab for lab in LAB_REGISTRY}

__all__ = [
    "FlagDef",
    "HintDef",
    "ChallengeDef",
    "LabDefinition",
    "LAB_REGISTRY",
    "REGISTRY_BY_SLUG",
    "REGISTRY_BY_ID",
    "STANDALONE_CHALLENGES",
]
