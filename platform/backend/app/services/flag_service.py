# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import hashlib
import subprocess
import textwrap
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.challenge import Challenge, ChallengeFlag, ChallengeSubmission, FlagType
from app.models.deployment import Deployment


@dataclass
class FlagContext:
    user_id: int
    team_id: int | None
    event_id: int | None
    deployment: Deployment | None = None


@dataclass
class ValidationResult:
    correct: bool
    already_solved: bool = False
    first_blood: bool = False
    points_awarded: int = 0


def check_already_solved(db: Session, challenge_id: int, user_id: int) -> bool:
    return (
        db.query(ChallengeSubmission)
        .filter(
            ChallengeSubmission.challenge_id == challenge_id,
            ChallengeSubmission.user_id == user_id,
            ChallengeSubmission.is_correct.is_(True),
        )
        .first()
        is not None
    )


def check_first_blood(db: Session, challenge_id: int, event_id: int | None) -> bool:
    q = db.query(ChallengeSubmission).filter(
        ChallengeSubmission.challenge_id == challenge_id,
        ChallengeSubmission.is_correct.is_(True),
    )
    if event_id is not None:
        q = q.filter(ChallengeSubmission.event_id == event_id)
    return q.count() == 0


def validate_flag(
    challenge: Challenge,
    submitted: str,
    context: FlagContext,
) -> ValidationResult:
    for flag_cfg in challenge.flags:
        result = _check_flag_config(flag_cfg, submitted, context)
        if result:
            return ValidationResult(correct=True)
    return ValidationResult(correct=False)


def _check_flag_config(flag_cfg: ChallengeFlag, submitted: str, context: FlagContext) -> bool:
    match flag_cfg.flag_type:
        case FlagType.STATIC:
            return _compare(submitted, flag_cfg.value or "", flag_cfg.case_sensitive)
        case FlagType.DYNAMIC:
            if context.deployment is None or context.deployment.dynamic_flag is None:
                return False
            return _compare(submitted, context.deployment.dynamic_flag, flag_cfg.case_sensitive)
        case FlagType.PER_USER:
            if flag_cfg.value is None:
                return False
            expected = flag_cfg.value.replace("{user_id}", str(context.user_id))
            return _compare(submitted, expected, flag_cfg.case_sensitive)
        case FlagType.PER_TEAM:
            if flag_cfg.value is None or context.team_id is None:
                return False
            expected = flag_cfg.value.replace("{team_id}", str(context.team_id))
            return _compare(submitted, expected, flag_cfg.case_sensitive)
        case _:
            return False


def _compare(submitted: str, expected: str, case_sensitive: bool) -> bool:
    if not case_sensitive:
        return submitted.strip().lower() == expected.strip().lower()
    return submitted.strip() == expected.strip()


def _hash_compare(submitted: str, stored_hash: str, hash_type: str) -> bool:
    fn = {"sha256": hashlib.sha256, "md5": hashlib.md5}.get(hash_type)
    if fn is None:
        return False
    return fn(submitted.strip().encode()).hexdigest() == stored_hash.lower()


def _run_sandboxed_script(script: str, submitted: str, context: FlagContext) -> bool:
    """Execute a custom validation script in a restricted subprocess."""
    wrapper = textwrap.dedent(f"""
        import sys, resource
        resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
        resource.setrlimit(resource.RLIMIT_AS, (64 * 1024 * 1024, 64 * 1024 * 1024))

        submitted = {submitted!r}
        user_id = {context.user_id!r}
        team_id = {context.team_id!r}
        event_id = {context.event_id!r}

        {script}

        print("CORRECT" if result else "WRONG")
    """)
    try:
        proc = subprocess.run(
            ["python3", "-c", wrapper],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return proc.stdout.strip() == "CORRECT"
    except (subprocess.TimeoutExpired, Exception):
        return False
