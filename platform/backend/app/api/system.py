# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models.deployment import Deployment, DeploymentStatus
from app.models.user import User
from app.services.docker_runtime import docker_service

router = APIRouter(prefix="/system", tags=["system"])


class HealthOut(BaseModel):
    docker: str
    database: str
    running_labs: int
    total_containers: int


@router.get("/health", response_model=HealthOut)
def health(
    db: Session = Depends(get_db),
) -> HealthOut:
    docker_ok = docker_service.ping()

    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except SQLAlchemyError:
        db_ok = False

    running_labs = (
        db.query(Deployment).filter(Deployment.status == DeploymentStatus.RUNNING).count()
    )

    all_containers = docker_service.get_all_octorig_containers()

    return HealthOut(
        docker="ok" if docker_ok else "error",
        database="ok" if db_ok else "error",
        running_labs=running_labs,
        total_containers=len(all_containers),
    )


@router.get("/containers")
def containers(_: User = Depends(require_admin)) -> list[dict]:
    """
    All octorig-* containers visible to Docker daemon — includes those
    started by the CLI that have no Deployment row in the database.
    """
    return docker_service.get_all_octorig_containers()


@router.get("/plugins")
def list_plugins(_: User = Depends(require_admin)) -> list[dict]:
    from app.plugins.registry import list_plugins as _list

    return _list()
