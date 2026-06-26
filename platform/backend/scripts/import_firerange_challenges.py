#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Import BreachSQL, StingXSS, and VaultGate challenge registries into the
platform challenge engine.

Run from platform/backend/:
    python scripts/import_firerange_challenges.py [--dry-run] [--reset]

Flags:
    --dry-run   Print what would be inserted without touching the database.
    --reset     Delete all existing firerange challenges before importing.
    --lab       Only import one lab: breachsql | stingxss | vaultgate
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# ── Path setup ────────────────────────────────────────────────────────────────
# Allow: python scripts/import_firerange_challenges.py from platform/backend/
_HERE = Path(__file__).resolve().parent
_BACKEND = _HERE.parent
_REPO_ROOT = _BACKEND.parent.parent  # OctoRig/

sys.path.insert(0, str(_BACKEND))         # app.* imports
sys.path.insert(0, str(_REPO_ROOT))       # labs.* imports (used below as direct path import)

# ── Registry imports (absolute path, no package __init__ needed) ──────────────
import importlib.util as _ilu  # noqa: E402


def _load_registry(relative: str) -> list[dict]:
    path = _REPO_ROOT / relative
    spec = _ilu.spec_from_file_location("_registry", path)
    mod = _ilu.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.CHALLENGES


# ── Difficulty maps ───────────────────────────────────────────────────────────

_BREACHSQL_DIFF: dict[int, str] = {
    1: "easy",
    2: "easy",
    3: "medium",
    4: "medium",
    5: "hard",
    6: "medium",   # PG tier-6 basics
    7: "medium",   # PG tier-7 intermediate
    8: "hard",     # PG tier-8 advanced
    9: "hard",     # PG tier-9 legend
    10: "medium",  # SQLite tier-10 basics
    11: "medium",  # SQLite tier-11 intermediate
    12: "hard",    # SQLite tier-12 legend
}

_STINGXSS_DIFF: dict[int, str] = {
    1: "easy",
    2: "easy",
    3: "medium",
    4: "medium",
    5: "hard",
    6: "hard",
    7: "insane",   # CSP bypass
    8: "insane",   # SSTI → XSS
    9: "hard",     # GraphQL XSS
    10: "hard",    # WebSocket XSS
    11: "hard",    # DOM advanced
}

_VAULTGATE_DIFF: dict[int, str] = {
    1: "easy",
    2: "medium",
    3: "medium",
    4: "hard",
    5: "hard",
    6: "hard",
    7: "hard",
    8: "insane",   # JWT tampering
}


def _slugify(prefix: str, challenge_id: str) -> str:
    """e.g. breachsql-my1a, stingxss-r1a, vaultgate-i1a"""
    return f"{prefix}-{challenge_id.lower()}"


def _estimated_minutes(difficulty: str, challenge_type_hint: str) -> int:
    """Rough estimate so the UI has something to show."""
    base = {"easy": 20, "medium": 45, "hard": 90, "insane": 180}.get(difficulty, 45)
    if "time" in challenge_type_hint.lower() or "blind" in challenge_type_hint.lower():
        base = int(base * 1.5)
    return base


def _build_tags(technique: str, extra: list[str]) -> list[str]:
    tags: list[str] = []
    for part in re.split(r"[,/→]", technique):
        t = part.strip().lower()
        if t:
            tags.append(t)
    tags.extend(e.lower() for e in extra if e)
    return list(dict.fromkeys(tags))  # deduplicate, preserve order


# ── Per-lab builders ──────────────────────────────────────────────────────────

def build_breachsql(raw: list[dict]) -> list[dict]:
    records = []
    for ch in raw:
        cid = ch["challenge_id"]
        diff = _BREACHSQL_DIFF.get(ch["tier"], "medium")
        technique = ch.get("technique", "")

        # derive sub-category tag from id prefix
        sub = "mysql" if cid.startswith("my") else "postgresql" if cid.startswith("pg") else "sqlite"

        rec: dict[str, Any] = {
            "slug": _slugify("breachsql", cid),
            "title": ch["title"],
            "description": ch["description"],
            "challenge_type": "flag",
            "difficulty": diff,
            "category": "sql-injection",
            "tags": _build_tags(technique, [sub, f"tier-{ch['tier']}"]),
            "skills": [sub, "sqli"],
            "points": ch["points"],
            "estimated_minutes": _estimated_minutes(diff, technique),
            "content": {
                "endpoint": ch.get("endpoint", ""),
                "ui_endpoint": ch.get("ui_endpoint"),
                "technique": technique,
                "lab": "BreachSQL Fire Range",
            },
            "flag": ch["flag"],
            "hint": ch.get("hint"),
        }
        records.append(rec)
    return records


def build_stingxss(raw: list[dict]) -> list[dict]:
    records = []
    for ch in raw:
        cid = ch["challenge_id"]
        diff = _STINGXSS_DIFF.get(ch["tier"], "medium")
        technique = ch.get("technique", "")

        # sub-category from technique
        if cid.startswith("r"):
            sub = "reflected-xss"
        elif cid.startswith("s"):
            sub = "stored-xss"
        elif cid.startswith("d"):
            sub = "dom-xss"
        elif cid.startswith("b"):
            sub = "blind-xss"
        elif cid.startswith("w"):
            sub = "waf-bypass"
        elif cid.startswith("c"):
            sub = "csp-bypass"
        elif cid.startswith("t"):
            sub = "ssti"
        elif cid.startswith("g"):
            sub = "graphql"
        elif cid.startswith("ws"):
            sub = "websocket"
        else:
            sub = "xss"

        rec: dict[str, Any] = {
            "slug": _slugify("stingxss", cid),
            "title": ch["title"],
            "description": ch["description"],
            "challenge_type": "flag",
            "difficulty": diff,
            "category": "xss",
            "tags": _build_tags(technique, [sub, f"tier-{ch['tier']}"]),
            "skills": [sub, "xss", "client-side"],
            "points": ch["points"],
            "estimated_minutes": _estimated_minutes(diff, technique),
            "content": {
                "endpoint": ch.get("endpoint", ""),
                "technique": technique,
                "lab": "StingXSS Range",
            },
            "flag": ch["flag"],
            "hint": ch.get("hint"),
        }
        records.append(rec)
    return records


def build_vaultgate(raw: list[dict]) -> list[dict]:
    records = []
    for ch in raw:
        cid = ch["challenge_id"]
        diff = _VAULTGATE_DIFF.get(ch["tier"], "medium")
        technique = ch.get("technique", "")

        if cid.startswith("i"):
            sub = "horizontal-idor"
        elif cid.startswith("v"):
            sub = "vertical-idor"
        elif cid.startswith("m"):
            sub = "method-bypass"
        elif cid.startswith("p"):
            sub = "parameter-pollution"
        elif cid.startswith("a"):
            sub = "mass-assignment"
        elif cid.startswith("j"):
            sub = "jwt"
        else:
            sub = "idor"

        rec: dict[str, Any] = {
            "slug": _slugify("vaultgate", cid),
            "title": ch["title"],
            "description": ch["description"],
            "challenge_type": "flag",
            "difficulty": diff,
            "category": "idor",
            "tags": _build_tags(technique, [sub, f"tier-{ch['tier']}"]),
            "skills": [sub, "access-control"],
            "points": ch["points"],
            "estimated_minutes": _estimated_minutes(diff, technique),
            "content": {
                "endpoint": ch.get("endpoint", ""),
                "technique": technique,
                "lab": "VaultGate IDOR Range",
            },
            "flag": ch["flag"],
            "hint": ch.get("hint"),
        }
        records.append(rec)
    return records


# ── Database insertion ────────────────────────────────────────────────────────

def _import_to_db(records: list[dict], dry_run: bool, reset_prefix: str | None) -> None:
    from app.database import SessionLocal
    from app.models.challenge import (
        Challenge,
        ChallengeDifficulty,
        ChallengeFlag,
        ChallengeHint,
        ChallengeType,
        FlagType,
    )

    db = SessionLocal()
    try:
        if reset_prefix:
            deleted = (
                db.query(Challenge)
                .filter(Challenge.slug.like(f"{reset_prefix}-%"))
                .all()
            )
            if deleted:
                print(f"  Deleting {len(deleted)} existing '{reset_prefix}' challenges…")
                if not dry_run:
                    for ch in deleted:
                        db.delete(ch)
                    db.commit()
                else:
                    print("  [dry-run] skipped deletion")

        inserted = skipped = 0
        for rec in records:
            slug = rec["slug"]
            existing = db.query(Challenge).filter(Challenge.slug == slug).first()
            if existing:
                skipped += 1
                continue

            if dry_run:
                print(f"  [dry-run] would insert: {slug} — {rec['title']!r} ({rec['points']} pts)")
                inserted += 1
                continue

            ch = Challenge(
                slug=slug,
                title=rec["title"],
                description=rec["description"],
                challenge_type=ChallengeType(rec["challenge_type"]),
                difficulty=ChallengeDifficulty(rec["difficulty"]),
                category=rec["category"],
                tags=rec["tags"],
                skills=rec["skills"],
                points=rec["points"],
                estimated_minutes=rec["estimated_minutes"],
                content=rec["content"],
                is_active=True,
                is_archived=False,
                version=1,
            )
            db.add(ch)
            db.flush()

            flag = ChallengeFlag(
                challenge_id=ch.id,
                flag_type=FlagType.STATIC,
                value=rec["flag"],
                case_sensitive=True,
            )
            db.add(flag)

            if rec.get("hint"):
                hint = ChallengeHint(
                    challenge_id=ch.id,
                    order_num=1,
                    content=rec["hint"],
                    cost=0,
                )
                db.add(hint)

            db.commit()
            inserted += 1
            print(f"  ✓ {slug}")

        print(f"\n  Inserted: {inserted}  Skipped (already exists): {skipped}")
    finally:
        db.close()


# ── CLI ────────────────────────────────────────────────────────────────────────

LABS = {
    "breachsql": ("labs/firerange/core/registry.py", build_breachsql),
    "stingxss":  ("labs/stingxss/core/registry.py",  build_stingxss),
    "vaultgate": ("labs/vaultgate/core/registry.py",  build_vaultgate),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing to DB")
    parser.add_argument("--reset", action="store_true", help="Delete existing firerange challenges before import")
    parser.add_argument("--lab", choices=list(LABS), help="Import only one specific lab")
    args = parser.parse_args()

    targets = {args.lab: LABS[args.lab]} if args.lab else LABS

    total_records: list[dict] = []

    for lab_name, (registry_path, builder) in targets.items():
        print(f"\n── {lab_name.upper()} ──")
        try:
            raw = _load_registry(registry_path)
        except Exception as exc:
            print(f"  ERROR loading registry: {exc}")
            continue

        records = builder(raw)
        print(f"  Loaded {len(records)} challenges from registry")

        reset_prefix = lab_name if args.reset else None
        _import_to_db(records, dry_run=args.dry_run, reset_prefix=reset_prefix)
        total_records.extend(records)

    print(f"\nTotal challenges processed: {len(total_records)}")
    if args.dry_run:
        print("[dry-run mode — no data was written]")


if __name__ == "__main__":
    main()
