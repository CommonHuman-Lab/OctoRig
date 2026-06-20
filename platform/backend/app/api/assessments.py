# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Assessment Mode API — admin management + candidate-facing endpoints."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Response
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.config import settings
from app.core.exceptions import bad_request, conflict, credentials_exception, forbidden_exception, not_found
from app.core.security import create_access_token, generate_opaque_token, hash_password, hash_token
from app.labs.registry import REGISTRY_BY_SLUG
from app.models.assessment import Assessment, AssessmentInvite, AssessmentReport
from app.models.challenge import ChallengeSubmission
from app.models.deployment import Deployment, DeploymentStatus, DeploymentVisibility
from app.models.lab_template import LabTemplate
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentInviteCreate,
    AssessmentInviteResponse,
    AssessmentInviteWithProgress,
    AssessmentResponse,
    AssessmentUpdate,
    CandidateAssessmentStatus,
    CandidateLabInfo,
    FlagSolve,
    InviteAcceptRegister,
    InviteLandingResponse,
    InviteStatus,
    ReportResponse,
    ReportSubmit,
)
from app.schemas.auth import TokenResponse
from app.services import audit_service
from app.services.audit_service import write_audit
from app.services.challenge_rendering import render_access_info
from app.services.deployment_provisioning import prepare_deployment
from app.services.lab_service import start_lab, stop_lab
from app.services.settings_service import get_settings
from app.services.team_service import ensure_personal_team

admin_router = APIRouter(prefix="/admin/assessments", tags=["admin-assessments"])
candidate_router = APIRouter(prefix="/assessments", tags=["assessments"])

_COOKIE_NAME = "octorig_refresh_token"
_COOKIE_PATH = "/api/v1/auth"


# --- Helpers ---

def _compute_status(invite: AssessmentInvite) -> InviteStatus:
    if invite.is_revoked:
        return "revoked"
    if invite.accepted_at is None:
        return "pending"
    if invite.started_at is None:
        return "accepted"
    if invite.completed_at is not None:
        return "completed"
    now = datetime.now(timezone.utc)
    if invite.expires_at and invite.expires_at.replace(tzinfo=timezone.utc) < now:
        return "expired"
    return "active"


def _invite_response(invite: AssessmentInvite) -> AssessmentInviteResponse:
    return AssessmentInviteResponse(
        id=invite.id,
        assessment_id=invite.assessment_id,
        email=invite.email,
        candidate_name=invite.candidate_name,
        token=invite.token,
        user_id=invite.user_id,
        accepted_at=invite.accepted_at,
        started_at=invite.started_at,
        expires_at=invite.expires_at,
        completed_at=invite.completed_at,
        deployment_ids=invite.deployment_ids or [],
        is_revoked=invite.is_revoked,
        status=_compute_status(invite),
    )


def _assessment_response(assessment: Assessment, db: Session) -> AssessmentResponse:
    total = db.query(AssessmentInvite).filter(
        AssessmentInvite.assessment_id == assessment.id
    ).count()
    active = db.query(AssessmentInvite).filter(
        AssessmentInvite.assessment_id == assessment.id,
        AssessmentInvite.is_revoked.is_(False),
        AssessmentInvite.started_at.isnot(None),
        AssessmentInvite.expires_at > datetime.now(timezone.utc),
    ).count()
    return AssessmentResponse(
        id=assessment.id,
        name=assessment.name,
        slug=assessment.slug,
        company_name=assessment.company_name,
        company_logo_url=assessment.company_logo_url,
        description=assessment.description,
        candidate_instructions=assessment.candidate_instructions,
        duration_hours=assessment.duration_hours,
        lab_slugs=assessment.lab_slugs or [],
        lab_display_names=assessment.lab_display_names or {},
        is_active=assessment.is_active,
        created_by_id=assessment.created_by_id,
        created_at=assessment.created_at,
        invite_count=total,
        active_invite_count=active,
    )


def _slugify(name: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _issue_refresh_token(db: Session, user_id: int) -> str:
    from app.core.security import generate_opaque_token, hash_token
    raw = generate_opaque_token()
    expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    db.add(RefreshToken(user_id=user_id, token_hash=hash_token(raw), expires_at=expires))
    db.commit()
    return raw


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=not settings.debug,
        path=_COOKIE_PATH,
        max_age=settings.refresh_token_expire_days * 86_400,
    )


# --- Admin — CRUD ---

@admin_router.get("/", response_model=list[AssessmentResponse])
def list_assessments(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AssessmentResponse]:
    assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).all()
    return [_assessment_response(a, db) for a in assessments]


@admin_router.post("/", response_model=AssessmentResponse, status_code=201)
def create_assessment(
    payload: AssessmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    invalid = [s for s in payload.lab_slugs if s not in REGISTRY_BY_SLUG]
    if invalid:
        raise bad_request(f"Unknown lab slugs: {invalid}")

    slug = payload.slug or _slugify(payload.name)
    if db.query(Assessment).filter(Assessment.slug == slug).first():
        raise conflict(f"Assessment slug '{slug}' is already taken")

    assessment = Assessment(
        name=payload.name,
        slug=slug,
        company_name=payload.company_name,
        company_logo_url=payload.company_logo_url,
        description=payload.description,
        candidate_instructions=payload.candidate_instructions,
        duration_hours=payload.duration_hours,
        lab_slugs=payload.lab_slugs,
        lab_display_names=payload.lab_display_names or {},
        is_active=True,
        created_by_id=current_user.id,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return _assessment_response(assessment, db)


@admin_router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    assessment = db.get(Assessment, assessment_id)
    if assessment is None:
        raise not_found("Assessment")
    return _assessment_response(assessment, db)


@admin_router.patch("/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(
    assessment_id: int,
    payload: AssessmentUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    assessment = db.get(Assessment, assessment_id)
    if assessment is None:
        raise not_found("Assessment")

    if payload.lab_slugs is not None:
        invalid = [s for s in payload.lab_slugs if s not in REGISTRY_BY_SLUG]
        if invalid:
            raise bad_request(f"Unknown lab slugs: {invalid}")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(assessment, field, value)

    db.commit()
    db.refresh(assessment)
    return _assessment_response(assessment, db)


@admin_router.delete("/{assessment_id}", status_code=204)
def delete_assessment(
    assessment_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    assessment = db.get(Assessment, assessment_id)
    if assessment is None:
        raise not_found("Assessment")

    active_count = db.query(AssessmentInvite).filter(
        AssessmentInvite.assessment_id == assessment_id,
        AssessmentInvite.is_revoked.is_(False),
        AssessmentInvite.started_at.isnot(None),
        AssessmentInvite.expires_at > datetime.now(timezone.utc),
    ).count()
    if active_count > 0:
        raise bad_request("Cannot delete an assessment with active candidates")

    db.delete(assessment)
    db.commit()


# --- Admin — Invites ---

@admin_router.get("/{assessment_id}/invites", response_model=list[AssessmentInviteResponse])
def list_invites(
    assessment_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AssessmentInviteResponse]:
    if db.get(Assessment, assessment_id) is None:
        raise not_found("Assessment")
    invites = db.query(AssessmentInvite).filter(
        AssessmentInvite.assessment_id == assessment_id
    ).order_by(AssessmentInvite.id.desc()).all()
    return [_invite_response(i) for i in invites]


@admin_router.get("/{assessment_id}/progress", response_model=list[AssessmentInviteWithProgress])
def list_candidate_progress(
    assessment_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AssessmentInviteWithProgress]:
    assessment = db.get(Assessment, assessment_id)
    if assessment is None:
        raise not_found("Assessment")

    invites = db.query(AssessmentInvite).filter(
        AssessmentInvite.assessment_id == assessment_id
    ).order_by(AssessmentInvite.id.desc()).all()

    from app.models.challenge import Challenge

    user_ids = [i.user_id for i in invites if i.user_id is not None]
    subs_by_user: dict[int, list[FlagSolve]] = {}
    if user_ids:
        rows = (
            db.query(ChallengeSubmission, Challenge)
            .join(Challenge, Challenge.id == ChallengeSubmission.challenge_id)
            .join(LabTemplate, LabTemplate.id == Challenge.lab_template_id)
            .filter(
                ChallengeSubmission.user_id.in_(user_ids),
                ChallengeSubmission.is_correct.is_(True),
                LabTemplate.slug.in_(assessment.lab_slugs),
            )
            .all()
        )
        for sub, ch in rows:
            subs_by_user.setdefault(sub.user_id, []).append(FlagSolve(
                challenge_slug=ch.slug,
                challenge_title=ch.title,
                points=ch.points,
                solved_at=sub.submitted_at,
            ))

    results: list[AssessmentInviteWithProgress] = []
    for invite in invites:
        flags_solved = subs_by_user.get(invite.user_id, [])
        base = _invite_response(invite)
        results.append(AssessmentInviteWithProgress(
            **base.model_dump(),
            flags_solved=flags_solved,
            score=sum(f.points for f in flags_solved),
            report_submitted=invite.report is not None,
            report_content=invite.report.content if invite.report else None,
        ))
    return results


@admin_router.post("/{assessment_id}/invites", response_model=AssessmentInviteResponse, status_code=201)
def create_invite(
    assessment_id: int,
    payload: AssessmentInviteCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AssessmentInviteResponse:
    assessment = db.get(Assessment, assessment_id)
    if assessment is None:
        raise not_found("Assessment")
    if not assessment.is_active:
        raise bad_request("Assessment is not active")

    existing = db.query(AssessmentInvite).filter(
        AssessmentInvite.assessment_id == assessment_id,
        AssessmentInvite.email == payload.email,
    ).first()
    if existing:
        raise conflict(f"An invite for '{payload.email}' already exists in this assessment")

    invite = AssessmentInvite(
        assessment_id=assessment_id,
        email=payload.email,
        candidate_name=payload.candidate_name,
        token=AssessmentInvite.generate_token(),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return _invite_response(invite)


@admin_router.delete("/{assessment_id}/invites/{invite_id}", status_code=204)
def revoke_invite(
    assessment_id: int,
    invite_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    invite = db.query(AssessmentInvite).filter(
        AssessmentInvite.id == invite_id,
        AssessmentInvite.assessment_id == assessment_id,
    ).first()
    if invite is None:
        raise not_found("Invite")
    invite.is_revoked = True
    db.commit()


@admin_router.get(
    "/{assessment_id}/invites/{invite_id}/progress",
    response_model=AssessmentInviteWithProgress,
)
def get_candidate_progress(
    assessment_id: int,
    invite_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AssessmentInviteWithProgress:
    invite = db.query(AssessmentInvite).filter(
        AssessmentInvite.id == invite_id,
        AssessmentInvite.assessment_id == assessment_id,
    ).first()
    if invite is None:
        raise not_found("Invite")

    assessment = db.get(Assessment, assessment_id)
    flags_solved: list[FlagSolve] = []
    score = 0
    report_submitted = False

    if invite.user_id is not None:
        from app.models.challenge import Challenge

        subs = (
            db.query(ChallengeSubmission, Challenge)
            .join(Challenge, Challenge.id == ChallengeSubmission.challenge_id)
            .join(LabTemplate, LabTemplate.id == Challenge.lab_template_id)
            .filter(
                ChallengeSubmission.user_id == invite.user_id,
                ChallengeSubmission.is_correct.is_(True),
                LabTemplate.slug.in_(assessment.lab_slugs),
            )
            .all()
        )
        for sub, ch in subs:
            flags_solved.append(FlagSolve(
                challenge_slug=ch.slug,
                challenge_title=ch.title,
                points=ch.points,
                solved_at=sub.submitted_at,
            ))
        score = sum(f.points for f in flags_solved)

    if invite.report is not None:
        report_submitted = True

    base = _invite_response(invite)
    return AssessmentInviteWithProgress(
        **base.model_dump(),
        flags_solved=flags_solved,
        score=score,
        report_submitted=report_submitted,
        report_content=invite.report.content if invite.report else None,
    )


# --- Candidate — public invite landing ---

@candidate_router.get("/invite/{token}", response_model=InviteLandingResponse)
def get_invite_landing(
    token: str,
    db: Session = Depends(get_db),
) -> InviteLandingResponse:
    invite = db.query(AssessmentInvite).filter(AssessmentInvite.token == token).first()
    if invite is None or invite.is_revoked:
        raise not_found("Invite")

    assessment = invite.assessment
    site = get_settings(db)
    company_name = assessment.company_name or site.company_name
    company_logo_url = assessment.company_logo_url or site.company_logo_url

    return InviteLandingResponse(
        assessment_name=assessment.name,
        company_name=company_name,
        company_logo_url=company_logo_url,
        candidate_instructions=assessment.candidate_instructions,
        lab_count=len(assessment.lab_slugs or []),
        duration_hours=assessment.duration_hours,
        candidate_name=invite.candidate_name,
        status=_compute_status(invite),
    )


# --- Candidate — accept invite (register or link existing account) ---

@candidate_router.post("/invite/{token}/accept", response_model=TokenResponse, status_code=201)
def accept_invite(
    token: str,
    payload: InviteAcceptRegister,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Register a new candidate account and link it to this invite.
    Bypasses the global registration_open gate since the invite IS the
    authorization mechanism.
    """
    invite = db.query(AssessmentInvite).filter(AssessmentInvite.token == token).first()
    if invite is None or invite.is_revoked:
        raise not_found("Invite")

    if invite.user_id is not None:
        raise conflict("This invite has already been accepted")

    if len(payload.password) < 8:
        raise bad_request("Password must be at least 8 characters")
    if db.query(User).filter(User.username == payload.username).first():
        raise conflict(f"Username '{payload.username}' is already taken")

    user = User(
        username=payload.username,
        email=invite.email,
        hashed_password=hash_password(payload.password),
        is_active=True,
        is_candidate=True,
    )
    db.add(user)
    db.flush()

    ensure_personal_team(db, user)

    invite.user_id = user.id
    invite.accepted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    ip = request.client.host if request.client else None
    write_audit(db, action="assessment.candidate_registered", user_id=user.id, ip=ip,
                detail={"assessment_id": invite.assessment_id, "invite_id": invite.id})

    raw_refresh = _issue_refresh_token(db, user.id)
    _set_refresh_cookie(response, raw_refresh)

    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.access_token_expire_minutes * 60,
    )


# --- Candidate — start assessment (deploy labs, set timer) ---

@candidate_router.post("/me/start", response_model=CandidateAssessmentStatus)
def start_assessment(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CandidateAssessmentStatus:
    if not current_user.is_candidate:
        raise forbidden_exception

    invite = db.query(AssessmentInvite).filter(
        AssessmentInvite.user_id == current_user.id,
        AssessmentInvite.is_revoked.is_(False),
    ).first()
    if invite is None:
        raise not_found("Assessment invite")
    if invite.accepted_at is None:
        raise bad_request("Invite has not been accepted")

    if invite.started_at is not None:
        return _build_candidate_status(invite, db)

    now = datetime.now(timezone.utc)
    invite.started_at = now
    invite.expires_at = now + timedelta(hours=invite.assessment.duration_hours)
    db.flush()

    assessment = invite.assessment
    deployment_ids: list[int] = []

    for slug in (assessment.lab_slugs or []):
        template = db.query(LabTemplate).filter(LabTemplate.slug == slug).first()
        if template is None:
            continue
        lab_def = REGISTRY_BY_SLUG.get(slug)
        if lab_def is None:
            continue

        deployment = prepare_deployment(
            db,
            template,
            lab_def,
            started_by_id=current_user.id,
            instance_for_user_id=current_user.id,
            auto_destroy_at=invite.expires_at,
            visibility=DeploymentVisibility.PRIVATE,
        )
        deployment_ids.append(deployment.id)
        background_tasks.add_task(start_lab, deployment.id, current_user.id)

    invite.deployment_ids = deployment_ids
    db.commit()
    db.refresh(invite)

    write_audit(db, action="assessment.started", user_id=current_user.id,
                detail={"assessment_id": assessment.id, "invite_id": invite.id})

    return _build_candidate_status(invite, db)


# --- Candidate — workspace status ---

@candidate_router.get("/me", response_model=CandidateAssessmentStatus)
def get_assessment_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CandidateAssessmentStatus:
    if not current_user.is_candidate:
        raise forbidden_exception

    invite = db.query(AssessmentInvite).filter(
        AssessmentInvite.user_id == current_user.id,
        AssessmentInvite.is_revoked.is_(False),
    ).first()
    if invite is None:
        raise not_found("Assessment invite")

    return _build_candidate_status(invite, db)


def _build_candidate_status(invite: AssessmentInvite, db: Session) -> CandidateAssessmentStatus:
    assessment = invite.assessment
    site = get_settings(db)
    company_name = assessment.company_name or site.company_name
    company_logo_url = assessment.company_logo_url or site.company_logo_url

    now = datetime.now(timezone.utc)
    time_remaining: Optional[int] = None
    if invite.expires_at:
        expires_aware = invite.expires_at.replace(tzinfo=timezone.utc)
        delta = (expires_aware - now).total_seconds()
        time_remaining = max(0, int(delta))

    display_names: dict = assessment.lab_display_names or {}
    labs: list[CandidateLabInfo] = []
    for i, slug in enumerate(assessment.lab_slugs or []):
        display_name = display_names.get(slug) or slug.capitalize()
        deployment_id = (invite.deployment_ids or [None])[i] if i < len(invite.deployment_ids or []) else None

        dep_status = None
        access_info = []
        if deployment_id is not None:
            dep = db.get(Deployment, deployment_id)
            if dep:
                dep_status = dep.status
                if dep.status == DeploymentStatus.RUNNING:
                    access_info = dep.access_info or []
                    if not access_info:
                        template = db.get(LabTemplate, dep.lab_template_id)
                        if template:
                            access_info = render_access_info(template.access_info or [])

        labs.append(CandidateLabInfo(
            display_name=display_name,
            slug=slug,
            deployment_id=deployment_id,
            status=dep_status,
            access_info=access_info,
        ))

    report = invite.report
    return CandidateAssessmentStatus(
        assessment_name=assessment.name,
        company_name=company_name,
        company_logo_url=company_logo_url,
        candidate_instructions=assessment.candidate_instructions,
        started_at=invite.started_at,
        expires_at=invite.expires_at,
        completed_at=invite.completed_at,
        time_remaining_seconds=time_remaining,
        labs=labs,
        report_submitted=report is not None,
        report_content=report.content if report else None,
    )


# --- Candidate — report submission ---

@candidate_router.post("/me/report", response_model=ReportResponse)
def submit_report(
    payload: ReportSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportResponse:
    if not current_user.is_candidate:
        raise forbidden_exception

    invite = db.query(AssessmentInvite).filter(
        AssessmentInvite.user_id == current_user.id,
        AssessmentInvite.is_revoked.is_(False),
    ).first()
    if invite is None:
        raise not_found("Assessment invite")
    if invite.started_at is None:
        raise bad_request("Assessment has not been started")
    if invite.completed_at is not None:
        raise bad_request("Assessment is complete — the report is locked")
    if invite.expires_at and invite.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        raise bad_request("Assessment has expired — the report is locked")

    if invite.report is not None:
        invite.report.content = payload.content
        invite.report.submitted_at = datetime.now(timezone.utc)
    else:
        report = AssessmentReport(invite_id=invite.id, content=payload.content)
        db.add(report)

    db.commit()
    db.refresh(invite)

    return ReportResponse(
        invite_id=invite.id,
        content=invite.report.content,
        submitted_at=invite.report.submitted_at,
    )


# --- Candidate — finish early ---

@candidate_router.post("/me/complete", response_model=CandidateAssessmentStatus)
def complete_assessment(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CandidateAssessmentStatus:
    if not current_user.is_candidate:
        raise forbidden_exception

    invite = db.query(AssessmentInvite).filter(
        AssessmentInvite.user_id == current_user.id,
        AssessmentInvite.is_revoked.is_(False),
    ).first()
    if invite is None:
        raise not_found("Assessment invite")
    if invite.started_at is None:
        raise bad_request("Assessment has not been started")

    if invite.completed_at is None:
        now = datetime.now(timezone.utc)
        invite.completed_at = now
        if invite.expires_at is None or invite.expires_at.replace(tzinfo=timezone.utc) > now:
            invite.expires_at = now
        db.commit()
        db.refresh(invite)

        for deployment_id in (invite.deployment_ids or []):
            background_tasks.add_task(stop_lab, deployment_id, current_user.id)

        write_audit(db, action="assessment.completed", user_id=current_user.id,
                    detail={"assessment_id": invite.assessment_id, "invite_id": invite.id})

    return _build_candidate_status(invite, db)
