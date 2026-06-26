# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import not_found
from app.core.permissions import is_privileged
from app.models.lab_template import LabTemplate
from app.models.user import User
from app.schemas.lab_template import DeploymentSummary, LabTemplateResponse
from app.services.challenge_rendering import render_access_info
from app.services.lab_service import get_active_deployment
from app.services.settings_service import get_settings

router = APIRouter(prefix="/labs", tags=["labs"])


def _enrich(template: LabTemplate, db: Session, current_user: User) -> LabTemplateResponse:
    active = get_active_deployment(db, template.id, started_by_id=current_user.id)
    current = DeploymentSummary.model_validate(active) if active else None
    data = LabTemplateResponse.model_validate(template)
    data.current_deployment = current
    # Template-level access_info has no deployment to point at, so it always renders as "not running"
    data.access_info = render_access_info(data.access_info)
    if get_settings(db).hide_lab_ports and not is_privileged(current_user, db):
        data.exposed_ports = {}
    return data


@router.get("/", response_model=list[LabTemplateResponse])
def list_labs(
    category: str | None = Query(None, description="world | firerange | thirdparty"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LabTemplateResponse]:
    q = db.query(LabTemplate).filter(LabTemplate.is_active == True)  # noqa: E712
    if category:
        q = q.filter(LabTemplate.category == category)
    templates = q.order_by(LabTemplate.id).all()
    return [_enrich(t, db, current_user) for t in templates]


@router.get("/{lab_id}", response_model=LabTemplateResponse)
def get_lab(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTemplateResponse:
    template = db.get(LabTemplate, lab_id)
    if template is None:
        raise not_found("Lab")
    return _enrich(template, db, current_user)
