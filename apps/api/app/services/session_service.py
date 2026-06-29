import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.auth import SqlAlchemySessionRepository, SqlAlchemyAuditLogRepository
from app.models.user import Session, AuditLog

class SessionService:
    """Session telemetry tracking and token revocation manager."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repo = SqlAlchemySessionRepository(db)
        self.audit_repo = SqlAlchemyAuditLogRepository(db)
        
    async def list_active_sessions(self, user_id: uuid.UUID) -> Sequence[Session]:
        """Lists active, non-revoked session logs for a user."""
        return await self.session_repo.get_active_sessions(user_id)
        
    async def revoke_session(self, session_id: uuid.UUID, user_id: uuid.UUID, ip: str = None, ua: str = None) -> bool:
        """Revokes a specific active session."""
        session = await self.session_repo.get(session_id)
        if session and session.user_id == user_id and not session.revoked:
            session.revoked = True
            await self.session_repo.update(session)
            
            # Log audit trail event
            await self.audit_repo.create(AuditLog(
                actor=str(user_id), entity_name="Session", entity_id=session_id,
                action="SESSION_REVOKED", ip_address=ip, user_agent=ua
            ))
            return True
        return False
        
    async def revoke_all_sessions(self, user_id: uuid.UUID, ip: str = None, ua: str = None) -> int:
        """Revokes all active sessions for a user, forcing a complete logout across all devices."""
        active = await self.session_repo.get_active_sessions(user_id)
        count = 0
        for session in active:
            session.revoked = True
            await self.session_repo.update(session)
            count += 1
            
        if count > 0:
            await self.audit_repo.create(AuditLog(
                actor=str(user_id), entity_name="User", entity_id=user_id,
                action="ALL_SESSIONS_REVOKED", ip_address=ip, user_agent=ua
            ))
            
        return count
