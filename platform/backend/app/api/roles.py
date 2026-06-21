# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.api.deps import get_db, get_role_or_404, require_admin
from app.core.db_helpers import raise_if_exists
from app.core.exceptions import bad_request
from app.models.role import PlatformRole
from app.models.user import User
from app.schemas.admin import PlatformRoleCreate, PlatformRoleResponse, PlatformRoleUpdate

router = APIRouter(prefix="/admin/roles", tags=["admin-roles"])


@router.get("/", response_model=list[PlatformRoleResponse])
def list_roles(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[PlatformRoleResponse]:
    roles = db.query(PlatformRole).order_by(PlatformRole.slug.asc()).all()
    return [PlatformRoleResponse.model_validate(r) for r in roles]


@router.post("/", response_model=PlatformRoleResponse, status_code=201)
def create_role(
    payload: PlatformRoleCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PlatformRoleResponse:
    raise_if_exists(db, PlatformRole, f"Role slug '{payload.slug}' already exists", slug=payload.slug)
    role = PlatformRole(
        slug=payload.slug,
        display_name=payload.display_name,
        description=payload.description,
        permissions=payload.permissions,
        is_default=payload.is_default,
        is_system=False,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return PlatformRoleResponse.model_validate(role)


@router.get("/{slug}", response_model=PlatformRoleResponse)
def get_role(
    role: PlatformRole = Depends(get_role_or_404),
    _: User = Depends(require_admin),
) -> PlatformRoleResponse:
    return PlatformRoleResponse.model_validate(role)


@router.patch("/{slug}", response_model=PlatformRoleResponse)
def update_role(
    payload: PlatformRoleUpdate,
    role: PlatformRole = Depends(get_role_or_404),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PlatformRoleResponse:
    if role.slug == "admin":
        raise bad_request("The admin role cannot be edited")

    if payload.display_name is not None:
        role.display_name = payload.display_name
    if payload.description is not None:
        role.description = payload.description
    if payload.permissions is not None:
        role.permissions = payload.permissions
    if payload.is_default is not None:
        role.is_default = payload.is_default

    db.commit()
    db.refresh(role)
    return PlatformRoleResponse.model_validate(role)


@router.delete("/{slug}", status_code=204)
def delete_role(
    role: PlatformRole = Depends(get_role_or_404),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    if role.is_system:
        raise bad_request("System roles cannot be deleted")
    db.delete(role)
    db.commit()
