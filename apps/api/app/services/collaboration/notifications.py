import uuid
from datetime import datetime, timezone
from typing import Optional, Sequence, List
from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Notification

class NotificationsService:
    """Manages queries, unread calculations, and status updates for user alerts."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_user_notifications(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 50, only_unread: bool = False
    ) -> Sequence[Notification]:
        """Retrieves list of notifications belonging to a specific user, sorted by date."""
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.deleted_at == None
        ).order_by(desc(Notification.created_at)).offset(skip).limit(limit)
        
        if only_unread:
            stmt = stmt.where(Notification.read_at == None)
            
        return (await self.db.execute(stmt)).scalars().all()

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """Calculates total unread alerts pending for a user."""
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.read_at == None,
            Notification.deleted_at == None
        )
        return (await self.db.execute(stmt)).scalar() or 0

    async def mark_as_read(self, user_id: uuid.UUID, notification_ids: List[uuid.UUID]) -> int:
        """Marks specific notification records as read."""
        if not notification_ids:
            return 0
            
        stmt = update(Notification).where(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id,
            Notification.read_at == None,
            Notification.deleted_at == None
        ).values(read_at=datetime.now(timezone.utc)).execution_options(synchronize_session="fetch")
        
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        """Marks all pending unread notifications belonging to a user as read."""
        stmt = update(Notification).where(
            Notification.user_id == user_id,
            Notification.read_at == None,
            Notification.deleted_at == None
        ).values(read_at=datetime.now(timezone.utc)).execution_options(synchronize_session="fetch")
        
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount

    async def create_notification(
        self, user_id: uuid.UUID, category: str, title: str, message: str,
        sender_id: Optional[uuid.UUID] = None, data_json: Optional[dict] = None
    ) -> Notification:
        """Saves a notification alert to the database."""
        alert = Notification(
            user_id=user_id,
            type="IN_APP",
            category=category,
            title=title,
            message=message,
            sender_id=sender_id,
            data_json=data_json or {}
        )
        self.db.add(alert)
        await self.db.flush()
        return alert
