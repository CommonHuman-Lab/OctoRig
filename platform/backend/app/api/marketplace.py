# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.models.marketplace import PackageType
from app.models.user import User
from app.services.marketplace_service import (
    install_package,
    list_packages,
    uninstall_package,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


class PackageOut(BaseModel):
    id: int
    slug: str
    name: str
    version: str
    package_type: PackageType
    description: str | None
    author: str | None
    is_verified: bool
    checksum: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[PackageOut])
def list_packages_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[PackageOut]:
    return list_packages(db)


@router.post("/install", response_model=PackageOut, dependencies=[Depends(require_admin)])
async def install_endpoint(
    file: UploadFile = File(..., description="Octopack ZIP file"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackageOut:
    zip_bytes = await file.read()
    pkg = install_package(db, zip_bytes, current_user.id)
    return pkg


@router.delete("/{package_id}", status_code=204, dependencies=[Depends(require_admin)])
def uninstall_endpoint(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    uninstall_package(db, package_id, current_user.id)
