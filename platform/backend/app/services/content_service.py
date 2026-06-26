# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import re
from datetime import UTC, datetime
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import bad_request, forbidden_exception, not_found
from app.database import get_db
from app.models.challenge import (
    Challenge,
    ChallengeDifficulty,
    ChallengeFlag,
    ChallengeHint,
    ChallengeType,
    FlagType,
)
from app.models.content import (
    ContentReview,
    ContentStatus,
    ContentSubmission,
    ContentType,
    ReviewVerdict,
)
from app.models.user import User
from app.services import audit_service

# ── Slug helpers ─────────────────────────────────────────────────────────────


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower().strip()).strip("-")
    return slug[:50]


def _unique_challenge_slug(db: Session, base: str) -> str:
    slug = base
    counter = 2
    while db.query(Challenge).filter(Challenge.slug == slug).first():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


# ── Body validation ───────────────────────────────────────────────────────────


def validate_challenge_body(body: dict) -> list[str]:
    errors = []
    if not body.get("description") or len(str(body["description"]).strip()) < 10:
        errors.append("description must be at least 10 characters")
    if body.get("difficulty") not in ("easy", "medium", "hard", "insane"):
        errors.append("difficulty must be easy, medium, hard, or insane")
    if not body.get("category") or not str(body["category"]).strip():
        errors.append("category is required")
    flags = body.get("flags", [])
    if not flags or not isinstance(flags, list):
        errors.append("at least one flag is required")
    else:
        for i, f in enumerate(flags):
            if not f.get("value") or not str(f["value"]).strip():
                errors.append(f"flag[{i}].value is required")
    if "points" in body:
        try:
            if int(body["points"]) < 1:
                errors.append("points must be at least 1")
        except (ValueError, TypeError):
            errors.append("points must be a positive integer")
    return errors


# ── Platform role guard ───────────────────────────────────────────────────────


def require_platform_role(role: str):
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        from app.core.permissions import is_privileged

        roles: list[str] = current_user.platform_roles or []
        if role not in roles and not is_privileged(current_user, db):
            raise forbidden_exception
        return current_user

    return dependency


# ── CRUD ──────────────────────────────────────────────────────────────────────


def create_submission(
    db: Session,
    author_id: int,
    content_type: ContentType,
    title: str,
    body: dict[str, Any],
) -> ContentSubmission:
    sub = ContentSubmission(
        author_id=author_id,
        content_type=content_type,
        title=title,
        body=body,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    audit_service.write_audit(
        db,
        audit_service.CONTENT_SUBMITTED,
        user_id=author_id,
        detail={"id": sub.id, "title": title},
    )
    return sub


def get_submission_or_404(db: Session, submission_id: int) -> ContentSubmission:
    sub = db.get(ContentSubmission, submission_id)
    if sub is None:
        raise not_found("Submission")
    return sub


def list_submissions(
    db: Session,
    author_id: int | None = None,
    status: str | None = None,
    statuses: list[str] | None = None,
) -> list[ContentSubmission]:
    q = db.query(ContentSubmission)
    if author_id is not None:
        q = q.filter(ContentSubmission.author_id == author_id)
    if statuses is not None:
        q = q.filter(ContentSubmission.status.in_([ContentStatus(s) for s in statuses]))
    elif status is not None:
        q = q.filter(ContentSubmission.status == ContentStatus(status))
    return q.order_by(ContentSubmission.created_at.desc()).all()


def update_submission(
    db: Session,
    submission: ContentSubmission,
    title: str | None,
    body: dict[str, Any] | None,
) -> ContentSubmission:
    if submission.status not in (ContentStatus.DRAFT, ContentStatus.REJECTED):
        raise bad_request("Can only edit drafts or rejected submissions")
    if title is not None:
        submission.title = title
    if body is not None:
        submission.body = body
    submission.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(submission)
    return submission


def submit_for_review(db: Session, submission: ContentSubmission) -> ContentSubmission:
    if submission.status not in (ContentStatus.DRAFT, ContentStatus.REJECTED):
        raise bad_request("Only drafts or rejected submissions can be submitted for review")
    if submission.content_type == ContentType.CHALLENGE:
        errors = validate_challenge_body(submission.body)
        if errors:
            raise bad_request("Body validation failed: " + "; ".join(errors))
    submission.status = ContentStatus.PENDING_REVIEW
    submission.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(submission)
    return submission


# ── Review workflow ───────────────────────────────────────────────────────────


def claim_review(db: Session, submission: ContentSubmission, reviewer_id: int) -> ContentSubmission:
    if submission.status != ContentStatus.PENDING_REVIEW:
        raise bad_request("Submission is not pending review")
    submission.status = ContentStatus.IN_REVIEW
    submission.reviewer_id = reviewer_id
    submission.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(submission)
    return submission


def record_review(
    db: Session,
    submission: ContentSubmission,
    reviewer_id: int,
    verdict: ReviewVerdict,
    comment: str | None,
) -> ContentReview:
    if submission.status not in (ContentStatus.IN_REVIEW,):
        raise bad_request("Submission is not in review")

    review = ContentReview(
        submission_id=submission.id,
        reviewer_id=reviewer_id,
        verdict=verdict,
        comment=comment,
    )
    db.add(review)

    if verdict == ReviewVerdict.APPROVED:
        submission.status = ContentStatus.APPROVED
    elif verdict == ReviewVerdict.REJECTED:
        submission.status = ContentStatus.REJECTED
        audit_service.write_audit(
            db, audit_service.CONTENT_REJECTED, user_id=reviewer_id, detail={"id": submission.id}
        )
    elif verdict == ReviewVerdict.NEEDS_CHANGES:
        submission.status = ContentStatus.DRAFT

    submission.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(review)
    return review


def publish_submission(
    db: Session, submission: ContentSubmission, publisher_id: int
) -> ContentSubmission:
    if submission.status != ContentStatus.APPROVED:
        raise bad_request("Only approved submissions can be published")

    if submission.content_type == ContentType.LAB:
        raise bad_request("Lab submissions require manual processing by an administrator")

    slug = None
    if submission.content_type == ContentType.CHALLENGE:
        body = submission.body
        errors = validate_challenge_body(body)
        if errors:
            raise bad_request("Body validation failed: " + "; ".join(errors))

        base_slug = f"community-{_slugify(submission.title)}"
        slug = _unique_challenge_slug(db, base_slug)

        ch_type = ChallengeType(body.get("challenge_type", "flag"))
        ch_content: dict = {}
        if ch_type == ChallengeType.SHORT_ANSWER and body.get("code_snippet"):
            ch_content["code_snippet"] = body["code_snippet"]
            ch_content["language"] = body.get("language", "text")

        challenge = Challenge(
            slug=slug,
            title=submission.title,
            description=body["description"],
            challenge_type=ch_type,
            difficulty=ChallengeDifficulty(body["difficulty"]),
            category=str(body["category"]).strip(),
            tags=[t.strip() for t in body.get("tags", []) if str(t).strip()],
            skills=[],
            author_id=submission.author_id,
            points=int(body.get("points", 100)),
            estimated_minutes=int(body["estimated_minutes"])
            if body.get("estimated_minutes")
            else None,
            content=ch_content,
            is_active=True,
            is_archived=False,
            version=1,
        )
        db.add(challenge)
        db.flush()

        for flag_data in body.get("flags", []):
            db.add(
                ChallengeFlag(
                    challenge_id=challenge.id,
                    flag_type=FlagType(flag_data.get("flag_type", "static")),
                    value=str(flag_data["value"]).strip(),
                    case_sensitive=bool(flag_data.get("case_sensitive", True)),
                )
            )

        for hint_data in body.get("hints", []):
            db.add(
                ChallengeHint(
                    challenge_id=challenge.id,
                    order_num=int(hint_data["order_num"]),
                    content=str(hint_data["content"]),
                    cost=int(hint_data.get("cost", 0)),
                )
            )

    submission.status = ContentStatus.PUBLISHED
    submission.updated_at = datetime.now(UTC)
    db.commit()
    audit_service.write_audit(
        db,
        audit_service.CONTENT_PUBLISHED,
        user_id=publisher_id,
        detail={"id": submission.id, "slug": slug},
    )
    db.refresh(submission)
    return submission
