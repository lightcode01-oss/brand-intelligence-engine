import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.models.user import User
from app.models.integration import WorkspaceIntegration, WorkspaceWebhook
from app.schemas.integration import (
    WorkspaceIntegrationCreate, WorkspaceIntegrationResponse,
    WorkspaceWebhookCreate, WorkspaceWebhookResponse
)
from app.schemas.response import StandardResponse, wrap_success_response
from app.services.integrations.registry import integration_registry

router = APIRouter(prefix="/integrations", tags=["Integrations"])

DEFAULT_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")

@router.get("/", response_model=StandardResponse[List[WorkspaceIntegrationResponse]])
async def list_integrations(
    request: Request,
    workspace_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[WorkspaceIntegrationResponse]]:
    """Retrieves all integrations configured for the workspace."""
    ws_id = workspace_id or DEFAULT_WS_ID
    stmt = select(WorkspaceIntegration).where(WorkspaceIntegration.workspace_id == ws_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return wrap_success_response(list(items), request, "Workspace integrations list retrieved.")

@router.post("/", response_model=StandardResponse[WorkspaceIntegrationResponse], status_code=status.HTTP_201_CREATED)
async def create_integration(
    request: Request,
    payload: WorkspaceIntegrationCreate,
    workspace_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[WorkspaceIntegrationResponse]:
    """Creates or updates integration settings for the workspace."""
    ws_id = workspace_id or DEFAULT_WS_ID
    
    # Check if provider already exists for workspace
    stmt = select(WorkspaceIntegration).where(
        WorkspaceIntegration.workspace_id == ws_id,
        WorkspaceIntegration.provider_slug == payload.provider_slug
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.settings_json = payload.settings_json
        existing.is_active = payload.is_active
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        return wrap_success_response(existing, request, "Workspace integration updated.")
    
    new_integration = WorkspaceIntegration(
        workspace_id=ws_id,
        provider_slug=payload.provider_slug,
        settings_json=payload.settings_json,
        is_active=payload.is_active
    )
    db.add(new_integration)
    await db.commit()
    await db.refresh(new_integration)
    return wrap_success_response(new_integration, request, "Workspace integration created.")

@router.delete("/{integration_id}", response_model=StandardResponse[dict])
async def delete_integration(
    request: Request,
    integration_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Removes integration settings."""
    stmt = delete(WorkspaceIntegration).where(WorkspaceIntegration.id == integration_id)
    await db.execute(stmt)
    await db.commit()
    return wrap_success_response({"id": integration_id, "deleted": True}, request, "Integration removed successfully.")

@router.post("/test/{integration_id}", response_model=StandardResponse[dict])
async def test_integration(
    request: Request,
    integration_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Triggers a verification test notification to verify connectivity."""
    stmt = select(WorkspaceIntegration).where(WorkspaceIntegration.id == integration_id)
    result = await db.execute(stmt)
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found.")
        
    payload = {
        "title": "Nomen Connection Test",
        "message": "This is a verification test from your Nomen Brand Intelligence platform.",
        "data_json": {"status": "testing", "authenticated": True}
    }
    
    success = await integration_registry.dispatch(
        integration.provider_slug,
        payload,
        integration.settings_json
    )
    
    if not success:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Integration delivery check failed.")
        
    return wrap_success_response({"success": True}, request, "Test notification dispatched.")

# Outbound Custom Webhooks CRUD
@router.get("/webhooks", response_model=StandardResponse[List[WorkspaceWebhookResponse]])
async def list_webhooks(
    request: Request,
    workspace_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[WorkspaceWebhookResponse]]:
    ws_id = workspace_id or DEFAULT_WS_ID
    stmt = select(WorkspaceWebhook).where(WorkspaceWebhook.workspace_id == ws_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return wrap_success_response(list(items), request, "Webhooks list retrieved.")

@router.post("/webhooks", response_model=StandardResponse[WorkspaceWebhookResponse], status_code=status.HTTP_201_CREATED)
async def create_webhook(
    request: Request,
    payload: WorkspaceWebhookCreate,
    workspace_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[WorkspaceWebhookResponse]:
    ws_id = workspace_id or DEFAULT_WS_ID
    
    # Check if duplicate url
    stmt = select(WorkspaceWebhook).where(
        WorkspaceWebhook.workspace_id == ws_id,
        WorkspaceWebhook.url == payload.url
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.secret_key = payload.secret_key
        existing.events_json = payload.events_json
        existing.is_active = payload.is_active
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        return wrap_success_response(existing, request, "Webhook subscription updated.")
        
    new_webhook = WorkspaceWebhook(
        workspace_id=ws_id,
        url=payload.url,
        secret_key=payload.secret_key,
        events_json=payload.events_json,
        is_active=payload.is_active
    )
    db.add(new_webhook)
    await db.commit()
    await db.refresh(new_webhook)
    return wrap_success_response(new_webhook, request, "Webhook subscription created.")

@router.delete("/webhooks/{webhook_id}", response_model=StandardResponse[dict])
async def delete_webhook(
    request: Request,
    webhook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    stmt = delete(WorkspaceWebhook).where(WorkspaceWebhook.id == webhook_id)
    await db.execute(stmt)
    await db.commit()
    return wrap_success_response({"id": webhook_id, "deleted": True}, request, "Webhook deleted successfully.")
