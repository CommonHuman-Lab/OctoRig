#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Smoke-test harness: start a world lab, run its solver, verify flags against the registry.

Usage:
    harness.py [--lab ID [--lab ID ...]]

With no --lab given, runs every lab registered in LABS below.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = REPO_ROOT / "platform" / "backend" / "app" / "labs" / "registry" / "world"
SOLVERS_DIR = Path(__file__).resolve().parent / "solvers"
OCTORIG_SH = REPO_ROOT / "octorig.sh"

# Static per-lab config. Container IPs come from each lab's labs/<slug>.sh
# (fixed --ip on a dedicated bridge network), so they don't need discovering
# at runtime. Extend this dict as later phases add solvers.
LABS: dict[int, dict[str, str]] = {
    1: {"slug": "rewindrange", "base_url": "http://172.28.1.2", "solver": "rewindrange"},
    2: {"slug": "tradefloor", "base_url": "http://172.28.2.2", "solver": "tradefloor"},
}


def load_expected_flags(slug: str) -> dict[str, list[str]]:
    """Parse a lab's registry file as an AST and pull out slug -> [flag values].

    Uses ast.literal_eval instead of importing the module so this doesn't need
    the platform backend's package hierarchy (`.._types` etc.) importable —
    the registry files are plain dict literals plus a type-only import.
    """
    path = REGISTRY_DIR / f"{slug}.py"
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Dict):
            lab = ast.literal_eval(node.value)
            return {
                chal["slug"]: [f["value"] for f in chal["flags"]]
                for chal in lab["challenges"]
            }
    raise ValueError(f"no lab dict literal found in {path}")


def load_solver(name: str):
    path = SOLVERS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"smoke_solver_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def octorig(action: str, lab_id: int) -> int:
    return subprocess.run(
        [str(OCTORIG_SH), action, str(lab_id)], cwd=REPO_ROOT
    ).returncode


def wait_healthy(base_url: str, timeout: int = 90) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(base_url, timeout=3)
            return True
        except urllib.error.HTTPError:
            # Any HTTP response (even 4xx/5xx) means the app is up and serving.
            return True
        except Exception:
            time.sleep(1)
    return False


def print_table(rows: list[tuple[str, str, str, str]]) -> None:
    headers = ("CHALLENGE", "RESULT", "FOUND", "EXPECTED")
    widths = [
        max(len(headers[i]), *(len(r[i]) for r in rows)) if rows else len(headers[i])
        for i in range(4)
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * w for w in widths)))
    for r in rows:
        print(fmt.format(*r))


def run_lab(lab_id: int) -> bool:
    cfg = LABS[lab_id]
    print(f"\n=== Lab {lab_id} ({cfg['slug']}) ===")
    expected = load_expected_flags(cfg["slug"])
    solver = load_solver(cfg["solver"])

    rc = octorig("start", lab_id)
    if rc != 0:
        print(f"FAIL: octorig.sh start {lab_id} exited {rc}")
        octorig("stop", lab_id)
        return False

    try:
        if not wait_healthy(cfg["base_url"]):
            print(f"FAIL: {cfg['base_url']} never became reachable")
            return False

        found = solver.solve(cfg["base_url"])

        rows = []
        all_ok = True
        for chal_slug, values in expected.items():
            got = found.get(chal_slug)
            passed = got is not None and any(
                got.strip().lower() == v.strip().lower() for v in values
            )
            all_ok = all_ok and passed
            rows.append((chal_slug, "PASS" if passed else "FAIL", got or "-", values[0]))

        print_table(rows)
        n_pass = sum(1 for r in rows if r[1] == "PASS")
        print(f"\n{n_pass}/{len(rows)} challenges solved.")
        return all_ok
    finally:
        octorig("stop", lab_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lab", type=int, action="append", dest="labs",
        help="Lab id to test (repeatable). Default: all labs with a solver.",
    )
    args = parser.parse_args()

    lab_ids = args.labs or sorted(LABS)
    unknown = [i for i in lab_ids if i not in LABS]
    if unknown:
        parser.error(f"no solver registered for lab id(s): {unknown}")

    results = {lab_id: run_lab(lab_id) for lab_id in lab_ids}

    print("\n=== Summary ===")
    for lab_id, ok in results.items():
        print(f"  Lab {lab_id} ({LABS[lab_id]['slug']}): {'PASS' if ok else 'FAIL'}")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
