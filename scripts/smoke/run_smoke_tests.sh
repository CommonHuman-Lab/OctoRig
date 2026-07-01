#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Run the OctoRig flag-solving smoke tests: starts each lab, runs its solver,
# diffs the recovered flags against the registry, then always stops the lab.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PYTHON="python3"
if [[ -x "/home/morten/DEV/.venv/bin/python3" ]]; then
  PYTHON="/home/morten/DEV/.venv/bin/python3"
fi

exec "$PYTHON" "${SCRIPT_DIR}/harness.py" "$@"
