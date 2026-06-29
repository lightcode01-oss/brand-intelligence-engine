import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.models.user import User, APIKey
from app.services.billing.api_key_service import APIKeyService
from app.schemas.response import StandardResponse, wrap_success_response
from pydantic import BaseModel

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

class APIKeyCreateRequest(BaseModel):
    name: str
    scopes: List[str]
    expiration_days: Optional[int] = None

class APIKeyResponseData(BaseModel):
    id: uuid.UUID
    name: str
    scopes: List[str]
    created_at: str
    expires_at: Optional[str] = None
    revoked_at: Optional[str] = None
    key_prefix: str

@router.get("/", response_model=StandardResponse[List[APIKeyResponseData]])
async def list_api_keys(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[APIKeyResponseData]]:
    """Lists all API keys configured by the user."""
    stmt = select(APIKey).where(
        APIKey.user_id == current_user.id,
        APIKey.deleted_at == None
    )
    result = await db.execute(stmt)
    keys = result.scalars().all()
    
    response_items = []
    for k in keys:
        scopes = k.scopes_json.get("scopes", [])
        response_items.append(
            APIKeyResponseData(
                id=k.id,
                name=k.name,
                scopes=scopes,
                created_at=k.created_at.isoformat(),
                expires_at=k.expires_at.isoformat() if k.expires_at else None,
                revoked_at=k.revoked_at.isoformat() if k.revoked_at else None,
                key_prefix="nm_live_..."
            )
        )
    return wrap_success_response(response_items, request, "API keys list retrieved.")

@router.post("/", response_model=StandardResponse[dict], status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: Request,
    payload: APIKeyCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Generates a secure API key, saves it and returns the raw key."""
    service = APIKeyService(db)
    raw_key = await service.create_key(
        user_id=current_user.id,
        name=payload.name,
        scopes=payload.scopes,
        expiration_days=payload.expiration_days
    )
    await db.commit()
    return wrap_success_response({"raw_key": raw_key}, request, "API key created successfully. Please record this key now; it will not be displayed again.")

@router.delete("/{key_id}", response_model=StandardResponse[dict])
async def revoke_api_key(
    request: Request,
    key_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Revokes/deletes an active API key."""
    from datetime import datetime, timezone
    stmt = update(APIKey).where(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).values(
        revoked_at=datetime.now(timezone.utc),
        deleted_at=datetime.now(timezone.utc)
    )
    await db.execute(stmt)
    await db.commit()
    return wrap_success_response({"id": key_id, "revoked": True}, request, "API key revoked successfully.")
