# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from typing import NotRequired, TypedDict


class FlagDef(TypedDict):
    value: str
    flag_type: str  # "static" | "dynamic" | "regex"
    case_sensitive: bool


class HintDef(TypedDict):
    order_num: int
    content: str
    cost: int  # 0 = free hint


class ChallengeDef(TypedDict):
    slug: str
    title: str
    description: str
    challenge_type: str  # "flag" | "short_answer" | "web" | "container" etc.
    difficulty: str  # "easy" | "medium" | "hard" | "insane"
    category: str
    tags: list[str]
    skills: list[str]
    points: int
    flags: list[FlagDef]
    hints: NotRequired[list[HintDef]]
    content: NotRequired[dict]  # type-specific extra data (code_snippet, language, etc.)
    requires_labs: NotRequired[list[str]]  # slugs of additional labs that must be running


class ResourceLimits(TypedDict, total=False):
    """Per-lab Docker resource constraints applied to every container in the lab.

    Keys map directly to docker-py containers.run() parameters.
    Omit a key to accept the platform default for that constraint.
    """

    mem_limit: str  # e.g. "512m", "2g"
    memswap_limit: str  # total memory+swap; set equal to mem_limit to disable swap
    cpu_quota: int  # microseconds per cpu_period (100 000); 50 000 = 50% of one core
    pids_limit: int  # max PIDs; -1 = unlimited (avoid)


class LabDefinition(TypedDict):
    id: int
    slug: str
    name: str
    description: str
    category: str  # "world" | "firerange" | "thirdparty"
    container_names: list[str]
    images: dict[str, str]  # role → image tag
    build_contexts: dict[str, str]  # role → path relative to OctoRig repo root
    start_order: list[str]  # roles in the order containers must start
    exposed_ports: dict[str, int]  # service name → port number
    # [{"key": "URL", "value": "..."}]; "{container_ip}" substituted per-deployment, see _scoped_access_info
    access_info: list[dict[str, str]]
    volume_names: list[str]
    env_vars: dict[str, str]
    requires_privileged: bool
    resource_limits: NotRequired[ResourceLimits]  # overrides platform defaults
    requires_internet: NotRequired[bool]  # allow outbound traffic (default: False)
    challenges: NotRequired[list[ChallengeDef]]
