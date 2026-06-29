"""Audit logging service: immutable security event recording."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.security import SecurityEvent


# Risk scoring heuristics by event type
_RISK_SCORES: dict[str, int] = {
    "LOGIN_SUCCESS": 0,
    "LOGIN_FAILED": 20,
    "LOGOUT": 0,
    "PASSWORD_CHANGED": 30,
    "PASSWORD_RESET": 40,
    "MFA_ENABLED": 10,
    "MFA_DISABLED": 50,
    "MFA_VERIFIED": 0,
    "MFA_FAILED": 25,
    "SESSION_REVOKED": 10,
    "API_KEY_CREATED": 15,
    "API_KEY_REVOKED": 10,
    "ROLE_CHANGED": 40,
    "EXPORT_REQUESTED": 5,
    "EXPORT_COMPLETED": 5,
    "ACCOUNT_LOCKED": 70,
    "ACCOUNT_UNLOCKED": 20,
    "SSO_LOGIN": 0,
    "DATA_EXPORT_REQUESTED": 10,
    "DATA_DELETION_REQUESTED": 80,
}


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def record(
        self,
        event_type: str,
        actor: str,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SecurityEvent:
        """Write an immutable security event record."""
        risk = _RISK_SCORES.get(event_type, 10)
        event = SecurityEvent(
            user_id=user_id,
            workspace_id=workspace_id,
            event_type=event_type,
            actor=actor,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=metadata or {},
            risk_score=risk,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def query_events(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        event_type: Optional[str] = None,
        since_hours: int = 72,
        limit: int = 100,
    ) -> list[dict]:
        """Retrieve recent security events filtered by context."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
        filters = [SecurityEvent.created_at >= cutoff]
        if user_id:
            filters.append(SecurityEvent.user_id == user_id)
        if workspace_id:
            filters.append(SecurityEvent.workspace_id == workspace_id)
        if event_type:
            filters.append(SecurityEvent.event_type == event_type)

        result = await self.db.execute(
            select(SecurityEvent)
            .where(and_(*filters))
            .order_by(SecurityEvent.created_at.desc())
            .limit(limit)
        )
        events = result.scalars().all()
        return [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "actor": e.actor,
                "ip_address": e.ip_address,
                "risk_score": e.risk_score,
                "metadata": e.metadata_json,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ]

    async def get_failed_login_count(self, actor: str, since_minutes: int = 15) -> int:
        """Count LOGIN_FAILED events for an actor in the recent window."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
        result = await self.db.execute(
            select(func.count()).select_from(SecurityEvent).where(
                SecurityEvent.actor == actor,
                SecurityEvent.event_type == "LOGIN_FAILED",
                SecurityEvent.created_at >= cutoff,
            )
        )
        return result.scalar_one() or 0

    async def high_risk_events_summary(
        self,
        workspace_id: Optional[uuid.UUID] = None,
        since_hours: int = 24,
    ) -> dict:
        """Aggregate counts of high-risk events for security dashboards."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
        filters = [
            SecurityEvent.created_at >= cutoff,
            SecurityEvent.risk_score >= 40,
        ]
        if workspace_id:
            filters.append(SecurityEvent.workspace_id == workspace_id)

        result = await self.db.execute(
            select(SecurityEvent).where(and_(*filters)).order_by(SecurityEvent.risk_score.desc())
        )
        events = result.scalars().all()
        type_counts: dict[str, int] = {}
        for e in events:
            type_counts[e.event_type] = type_counts.get(e.event_type, 0) + 1

        return {
            "total_high_risk_events": len(events),
            "breakdown": type_counts,
            "period_hours": since_hours,
        }

    async def get_compliance_report(
        self,
        workspace_id: uuid.UUID,
        since_days: int = 30,
    ) -> dict:
        """Generate a SOC 2 / ISO 27001 compliance activity summary."""
        since_hours = since_days * 24
        return {
            "workspace_id": str(workspace_id),
            "period_days": since_days,
            "high_risk_summary": await self.high_risk_events_summary(workspace_id, since_hours),
            "events": await self.query_events(workspace_id=workspace_id, since_hours=since_hours, limit=500),
        }
