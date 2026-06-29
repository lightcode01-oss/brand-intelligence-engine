import uuid
from typing import List, Optional
from fastapi import APIRouter, Request, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.models.user import User
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.user import NotificationResponse
from app.services.collaboration.notifications import NotificationsService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=StandardResponse[List[NotificationResponse]])
async def list_notifications(
    request: Request,
    only_unread: bool = Query(False, description="Filter for unread notifications only."),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[NotificationResponse]]:
    """Lists notifications belonging to the authenticated user."""
    service = NotificationsService(db)
    items = await service.list_user_notifications(current_user.id, skip=skip, limit=limit, only_unread=only_unread)
    return wrap_success_response(list(items), request, "Notifications list retrieved.")

@router.get("/unread-count", response_model=StandardResponse[dict])
async def get_unread_count(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Calculates total unread alerts pending for the user."""
    service = NotificationsService(db)
    count = await service.get_unread_count(current_user.id)
    return wrap_success_response({"unread_count": count}, request, "Unread count calculated.")

@router.put("/read", response_model=StandardResponse[dict])
async def mark_notifications_read(
    request: Request,
    notification_ids: List[uuid.UUID],
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Marks specific notifications as read."""
    service = NotificationsService(db)
    count = await service.mark_as_read(current_user.id, notification_ids)
    return wrap_success_response({"marked_count": count}, request, f"Marked {count} notifications as read.")

@router.put("/read-all", response_model=StandardResponse[dict])
async def mark_all_notifications_read(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Marks all pending notifications as read."""
    service = NotificationsService(db)
    count = await service.mark_all_as_read(current_user.id)
    return wrap_success_response({"marked_count": count}, request, f"Marked all {count} notifications as read.")
