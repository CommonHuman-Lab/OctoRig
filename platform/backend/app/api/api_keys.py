# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from typing import Optional

from fastapi import APIRouter, Depends

from app.api.deps import get_client_ip, get_current_user_or_api_key
from app.database import get_db
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyResponse
from app.services import api_key_service, audit_service
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.get("/", response_model=list[ApiKeyResponse])
def list_keys(
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
) -> list[ApiKeyResponse]:
    keys = api_key_service.list_api_keys(db, current_user)
    return [ApiKeyResponse.model_validate(k) for k in keys]


@router.post("/", response_model=ApiKeyCreated, status_code=201)
def create_key(
    payload: ApiKeyCreate,
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> ApiKeyCreated:
    key, raw_key = api_key_service.create_api_key(
        db, current_user, payload.name, payload.expires_at
    )
    audit_service.write_audit(
        db,
        action=audit_service.API_KEY_CREATED,
        user_id=current_user.id,
        detail={"name": payload.name},
        ip=ip,
    )
    return ApiKeyCreated(**ApiKeyResponse.model_validate(key).model_dump(), raw_key=raw_key)


@router.delete("/{key_id}", status_code=204)
def revoke_key(
    key_id: int,
    current_user: User = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    ip: Optional[str] = Depends(get_client_ip),
) -> None:
    api_key_service.revoke_api_key(db, current_user, key_id)
    audit_service.write_audit(
        db,
        action=audit_service.API_KEY_REVOKED,
        user_id=current_user.id,
        detail={"key_id": key_id},
        ip=ip,
    )
