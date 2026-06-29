import uuid
from typing import List
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.models.user import User
from app.schemas.response import StandardResponse, wrap_success_response
from app.services.collaboration.search import SearchService

router = APIRouter(prefix="/search", tags=["Global Search"])

@router.get("/", response_model=StandardResponse[dict])
async def search_workspace_entities(
    request: Request,
    workspace_id: uuid.UUID = Query(...),
    q: str = Query(..., min_length=1, description="Fuzzy match search term query string."),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Fuzzy matches workspaces projects, names, collections, and favorites."""
    service = SearchService(db)
    results = await service.search_all(current_user.id, workspace_id, q, skip=skip, limit=limit)
    return wrap_success_response(results, request, "Search query executed.")

@router.get("/recent", response_model=StandardResponse[List[str]])
async def list_recent_searches(
    request: Request,
    workspace_id: uuid.UUID = Query(...),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[str]]:
    """Retrieves list of recent unique queries searched by the user."""
    service = SearchService(db)
    items = await service.get_recent_searches(current_user.id, workspace_id, limit=limit)
    return wrap_success_response(items, request, "Recent searches retrieved.")
