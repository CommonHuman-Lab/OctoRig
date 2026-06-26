# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import not_found
from app.models.badge import UserBadge
from app.models.challenge import Challenge, ChallengeSubmission
from app.models.profile import PrivacyLevel, UserProfile
from app.models.scoring import ScoreTransaction
from app.models.team import TeamMember
from app.models.user import User


def _ensure_profile(db: Session, user_id: int) -> UserProfile:
    profile = db.get(UserProfile, user_id)
    if profile is None:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def ensure_profile_visible(db: Session, viewer_id: int, target_user_id: int) -> None:
    """Raise not_found if target_user_id's profile is PRIVATE and viewer isn't the owner.

    Mirrors the privacy check in get_profile() so badge/rank/score lookups by user_id
    can't be used as a side door around a private profile.
    """
    if viewer_id == target_user_id:
        return
    profile = _ensure_profile(db, target_user_id)
    if profile.privacy_level == PrivacyLevel.PRIVATE:
        raise not_found("User")


def get_profile(db: Session, username: str, viewer_id: int | None = None) -> dict[str, Any]:
    user = db.query(User).filter(User.username == username, User.is_active.is_(True)).first()
    if user is None:
        raise not_found("User")

    profile = _ensure_profile(db, user.id)

    is_own = viewer_id == user.id
    if profile.privacy_level == PrivacyLevel.PRIVATE and not is_own:
        raise not_found("Profile")

    total_points = int(
        db.query(func.coalesce(func.sum(ScoreTransaction.points), 0))
        .filter(ScoreTransaction.user_id == user.id, ScoreTransaction.event_id.is_(None))
        .scalar() or 0
    )
    solve_count = int(
        db.query(func.count(ChallengeSubmission.id))
        .filter(
            ChallengeSubmission.user_id == user.id,
            ChallengeSubmission.is_correct.is_(True),
        )
        .scalar() or 0
    )
    first_bloods = int(
        db.query(func.count(ChallengeSubmission.id))
        .filter(
            ChallengeSubmission.user_id == user.id,
            ChallengeSubmission.is_first_blood.is_(True),
        )
        .scalar() or 0
    )
    team_count = int(
        db.query(func.count(TeamMember.id))
        .filter(TeamMember.user_id == user.id)
        .scalar() or 0
    )

    badges = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user.id)
        .order_by(UserBadge.awarded_at.desc())
        .limit(12)
        .all()
    )

    recent_solves: list[dict] = []
    if profile.show_activity or is_own:
        rows = (
            db.query(ChallengeSubmission, Challenge)
            .join(Challenge, Challenge.id == ChallengeSubmission.challenge_id)
            .filter(
                ChallengeSubmission.user_id == user.id,
                ChallengeSubmission.is_correct.is_(True),
            )
            .order_by(ChallengeSubmission.submitted_at.desc())
            .limit(10)
            .all()
        )
        recent_solves = [
            {
                "challenge_id": sub.challenge_id,
                "challenge_title": ch.title,
                "challenge_slug": ch.slug,
                "points_awarded": sub.points_awarded,
                "submitted_at": sub.submitted_at.isoformat(),
                "is_first_blood": sub.is_first_blood,
            }
            for sub, ch in rows
        ]

    return {
        "user_id": user.id,
        "username": user.username,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "website_url": profile.website_url,
        "location": profile.location,
        "github_handle": profile.github_handle,
        "privacy_level": profile.privacy_level.value,
        "show_activity": profile.show_activity,
        "theme": profile.theme,
        "locale": profile.locale,
        "total_points": total_points,
        "solve_count": solve_count,
        "first_bloods": first_bloods,
        "team_count": team_count,
        "badges": [
            {
                "slug": ub.badge.slug,
                "name": ub.badge.name,
                "icon": ub.badge.icon,
                "awarded_at": ub.awarded_at.isoformat(),
            }
            for ub in badges
        ],
        "recent_solves": recent_solves,
    }


def update_profile(
    db: Session,
    user_id: int,
    bio: str | None = None,
    avatar_url: str | None = None,
    website_url: str | None = None,
    location: str | None = None,
    github_handle: str | None = None,
    privacy_level: str | None = None,
    show_activity: bool | None = None,
    theme: str | None = None,
    locale: str | None = None,
) -> UserProfile:
    profile = _ensure_profile(db, user_id)
    if bio is not None:
        profile.bio = bio
    if avatar_url is not None:
        profile.avatar_url = avatar_url
    if website_url is not None:
        profile.website_url = website_url
    if location is not None:
        profile.location = location
    if github_handle is not None:
        profile.github_handle = github_handle
    if privacy_level is not None:
        profile.privacy_level = PrivacyLevel(privacy_level)
    if show_activity is not None:
        profile.show_activity = show_activity
    if theme is not None:
        profile.theme = theme
    if locale is not None:
        profile.locale = locale
    profile.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(profile)
    return profile
