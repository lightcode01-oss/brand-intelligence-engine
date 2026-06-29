import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import AuditLog
from app.repositories.auth import SqlAlchemyAuditLogRepository

class AuditService:
    """Logs system, administrative, and workspace operations trail."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SqlAlchemyAuditLogRepository(db)

    async def log_action(
        self, actor: str, action: str, entity_name: str,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        entity_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """Saves a detailed audit log entry tracing action contexts."""
        log = AuditLog(
            actor=actor,
            action=action,
            entity_name=entity_name,
            workspace_id=workspace_id,
            project_id=project_id,
            entity_id=entity_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id
        )
        log = await self.repo.create(log)
        await self.db.flush()
        return log

    async def list_workspace_logs(self, workspace_id: uuid.UUID) -> Sequence[AuditLog]:
        """Lists historical audit logs belonging to a workspace."""
        return await self.repo.list_by_workspace(workspace_id)
        
    async def list_actor_logs(self, actor: str) -> Sequence[AuditLog]:
        """Lists historical logs belonging to a specific actor user email."""
        return await self.repo.list_by_actor(actor)
