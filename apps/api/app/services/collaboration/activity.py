import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collaboration import ActivityEvent
from app.repositories.collaboration import SqlAlchemyActivityEventRepository
from app.services.collaboration.websocket import manager

class ActivityService:
    """Tracks, logs, and broadcasts workspace activity streams in real time."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SqlAlchemyActivityEventRepository(db)

    async def log_activity(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID, action_type: str,
        description: str, metadata_json: Optional[dict] = None
    ) -> ActivityEvent:
        """Saves a workspace activity log and broadcasts the event over WebSocket."""
        event = ActivityEvent(
            workspace_id=workspace_id,
            user_id=user_id,
            action_type=action_type,
            description=description,
            metadata_json=metadata_json or {}
        )
        event = await self.repo.create(event)
        await self.db.flush()
        
        # Broadcast event
        await manager.broadcast_to_workspace(
            workspace_id=workspace_id,
            event="activity_event",
            data={
                "id": str(event.id),
                "action_type": action_type,
                "description": description,
                "user_id": str(user_id),
                "created_at": event.created_at.isoformat() if event.created_at else None
            }
        )
        return event

    async def list_workspace_activity(self, workspace_id: uuid.UUID, limit: int = 50) -> Sequence[ActivityEvent]:
        """Lists active historical workspace events sorted chronologically."""
        return await self.repo.list_by_workspace(workspace_id, limit=limit)
