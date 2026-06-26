# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from collections.abc import Callable
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.badge_catalog import SEED_CATALOG
from app.models.badge import AchievementRule, AchievementRuleType, BadgeDefinition, UserBadge
from app.models.challenge import ChallengeSubmission
from app.models.scoring import ScoreTransaction
from app.services import audit_service
from app.services.scoring_service import ScoreTransactionSource, award_points

# ── Rule evaluators ───────────────────────────────────────────────────────────

def _eval_solve_count(db: Session, user_id: int, config: dict[str, Any]) -> bool:
    from app.models.challenge import Challenge
    threshold = config.get("threshold", 1)
    category = config.get("category")
    q = (
        db.query(func.count(ChallengeSubmission.id))
        .filter(
            ChallengeSubmission.user_id == user_id,
            ChallengeSubmission.is_correct.is_(True),
        )
    )
    if category:
        q = (
            q.join(Challenge, ChallengeSubmission.challenge_id == Challenge.id)
            .filter(Challenge.category == category)
        )
    return (q.scalar() or 0) >= threshold


def _eval_first_blood(db: Session, user_id: int, config: dict[str, Any]) -> bool:
    threshold = config.get("threshold", 1)
    count = (
        db.query(func.count(ChallengeSubmission.id))
        .filter(
            ChallengeSubmission.user_id == user_id,
            ChallengeSubmission.is_correct.is_(True),
            ChallengeSubmission.is_first_blood.is_(True),
        )
        .scalar() or 0
    )
    return count >= threshold


def _eval_category_complete(db: Session, user_id: int, config: dict[str, Any]) -> bool:
    from app.models.challenge import Challenge
    category = config.get("category")
    if not category:
        return False
    total = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.category == category,
            Challenge.is_active.is_(True),
            Challenge.is_archived.is_(False),
        )
        .scalar() or 0
    )
    if total == 0:
        return False
    solved = (
        db.query(func.count(ChallengeSubmission.id))
        .join(Challenge, ChallengeSubmission.challenge_id == Challenge.id)
        .filter(
            ChallengeSubmission.user_id == user_id,
            ChallengeSubmission.is_correct.is_(True),
            Challenge.category == category,
        )
        .scalar() or 0
    )
    return solved >= total


def _eval_points_threshold(db: Session, user_id: int, config: dict[str, Any]) -> bool:
    threshold = config.get("threshold", 0)
    total = (
        db.query(func.coalesce(func.sum(ScoreTransaction.points), 0))
        .filter(ScoreTransaction.user_id == user_id)
        .scalar() or 0
    )
    return int(total) >= threshold


def _eval_manual(_db: Session, _user_id: int, _config: dict[str, Any]) -> bool:
    return False


_EVALUATORS: dict[AchievementRuleType, Callable] = {
    AchievementRuleType.SOLVE_COUNT:       _eval_solve_count,
    AchievementRuleType.FIRST_BLOOD:       _eval_first_blood,
    AchievementRuleType.STREAK_DAYS:       lambda *_: False,
    AchievementRuleType.CATEGORY_COMPLETE: _eval_category_complete,
    AchievementRuleType.POINTS_THRESHOLD:  _eval_points_threshold,
    AchievementRuleType.MANUAL:            _eval_manual,
}


# ── Badge award ───────────────────────────────────────────────────────────────

def _already_earned(db: Session, user_id: int, badge_id: int) -> bool:
    return (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
        .first()
    ) is not None


def award_badge(
    db: Session,
    user_id: int,
    badge: BadgeDefinition,
    awarded_by_id: int | None = None,
    note: str | None = None,
) -> UserBadge | None:
    if _already_earned(db, user_id, badge.id):
        return None

    ub = UserBadge(
        user_id=user_id,
        badge_id=badge.id,
        awarded_by_id=awarded_by_id,
        note=note,
    )
    db.add(ub)
    db.flush()

    if badge.points_value > 0:
        award_points(
            db,
            user_id=user_id,
            points=badge.points_value,
            source_type=ScoreTransactionSource.BADGE_AWARD,
            source_id=badge.id,
        )

    audit_service.write_audit(
        db,
        action=audit_service.BADGE_AWARDED,
        user_id=user_id,
        detail={"badge_slug": badge.slug, "badge_name": badge.name},
    )
    db.commit()
    return ub


# ── Evaluation entry point ────────────────────────────────────────────────────

def evaluate_achievements(db: Session, user_id: int) -> list[str]:
    """Check all active rules for user_id; award any newly-earned badges.

    Returns slugs of newly awarded badges.
    """
    rules: list[AchievementRule] = (
        db.query(AchievementRule)
        .join(BadgeDefinition, AchievementRule.badge_id == BadgeDefinition.id)
        .filter(AchievementRule.is_active.is_(True), BadgeDefinition.is_active.is_(True))
        .all()
    )

    awarded: list[str] = []
    evaluated_badges: set[int] = set()

    for rule in rules:
        badge = rule.badge
        if badge.id in evaluated_badges:
            continue
        if _already_earned(db, user_id, badge.id):
            evaluated_badges.add(badge.id)
            continue

        evaluator = _EVALUATORS.get(rule.rule_type)
        if evaluator is None:
            continue

        try:
            met = evaluator(db, user_id, rule.rule_config)
        except Exception:
            continue

        if met:
            result = award_badge(db, user_id, badge)
            if result:
                awarded.append(badge.slug)
            evaluated_badges.add(badge.id)

    return awarded


# ── Badge catalog seeding ─────────────────────────────────────────────────────

_RULE_CONFIG_FIXUPS: dict[str, dict] = {
    "sql-master": {"category": "sqli"},
}


def seed_badge_catalog(db: Session) -> int:
    """Insert built-in badges if they don't already exist. Returns count inserted."""
    for slug, correct_config in _RULE_CONFIG_FIXUPS.items():
        badge = db.query(BadgeDefinition).filter(BadgeDefinition.slug == slug).first()
        if badge and badge.rules and badge.rules[0].rule_config != correct_config:
            badge.rules[0].rule_config = correct_config
            db.commit()

    inserted = 0
    for entry in SEED_CATALOG:
        existing = db.query(BadgeDefinition).filter(BadgeDefinition.slug == entry["slug"]).first()
        if existing:
            continue
        badge = BadgeDefinition(
            slug=entry["slug"],
            name=entry["name"],
            description=entry["description"],
            icon=entry["icon"],
            category=entry["category"],
            points_value=entry["points_value"],
        )
        db.add(badge)
        db.flush()
        rule = AchievementRule(
            badge_id=badge.id,
            rule_type=entry["rule_type"],
            rule_config=entry["rule_config"],
        )
        db.add(rule)
        db.commit()
        inserted += 1
    return inserted
