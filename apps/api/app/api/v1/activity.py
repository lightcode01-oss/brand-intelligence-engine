import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.models.user import User
from app.schemas.response import StandardResponse, wrap_success_response
from app.services.collaboration.activity import ActivityService

router = APIRouter(prefix="/activity", tags=["Workspace Activity Feeds"])

class ActivityUserShort(BaseModel):
    id: uuid.UUID
    email: str

    class Config:
        from_attributes = True

class ActivityEventResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    action_type: str
    description: str
    metadata_json: dict
    created_at: datetime
    user: Optional[ActivityUserShort] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=StandardResponse[List[ActivityEventResponse]])
async def list_workspace_activity(
    request: Request,
    workspace_id: uuid.UUID = Query(...),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[ActivityEventResponse]]:
    """Retrieves chronological activity timeline feeds for a workspace."""
    service = ActivityService(db)
    items = await service.list_workspace_activity(workspace_id, limit=limit)
    return wrap_success_response(list(items), request, "Workspace activity feed retrieved.")
