"""Session management service: device-tracked sessions with revocation support."""
import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.models.security import UserSession

_SESSION_TTL_HOURS = 8


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _parse_user_agent(ua: Optional[str]) -> tuple[str, str]:
    """Rough UA parser returning (browser, os)."""
    if not ua:
        return "Unknown", "Unknown"
    browser = "Other"
    os_name = "Other"
    ua_l = ua.lower()
    if "chrome" in ua_l:
        browser = "Chrome"
    elif "firefox" in ua_l:
        browser = "Firefox"
    elif "safari" in ua_l:
        browser = "Safari"
    elif "edge" in ua_l:
        browser = "Edge"
    if "windows" in ua_l:
        os_name = "Windows"
    elif "mac" in ua_l:
        os_name = "macOS"
    elif "linux" in ua_l:
        os_name = "Linux"
    elif "android" in ua_l:
        os_name = "Android"
    elif "ios" in ua_l or "iphone" in ua_l:
        os_name = "iOS"
    return browser, os_name


class SessionManager:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(
        self,
        user_id: uuid.UUID,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        ttl_hours: int = _SESSION_TTL_HOURS,
    ) -> UserSession:
        """Persist a new device-tracked session record."""
        browser, os_name = _parse_user_agent(user_agent)
        now = datetime.now(timezone.utc)
        session = UserSession(
            user_id=user_id,
            token_hash=_hash_token(token),
            browser=browser,
            os=os_name,
            device_name=f"{browser} on {os_name}",
            ip_address=ip_address,
            is_active=True,
            last_seen_at=now,
            expires_at=now + timedelta(hours=ttl_hours),
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_active_sessions(self, user_id: uuid.UUID) -> list[dict]:
        """Return all active (non-revoked, non-expired) sessions for a user."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(UserSession).where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > now,
                    UserSession.deleted_at == None,
                )
            ).order_by(UserSession.last_seen_at.desc())
        )
        sessions = result.scalars().all()
        return [
            {
                "id": str(s.id),
                "device_name": s.device_name,
                "browser": s.browser,
                "os": s.os,
                "ip_address": s.ip_address,
                "country": s.country,
                "last_seen_at": s.last_seen_at.isoformat(),
                "expires_at": s.expires_at.isoformat(),
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]

    async def revoke_session(self, session_id: uuid.UUID, user_id: uuid.UUID, reason: str = "user_requested") -> bool:
        """Revoke a specific session by ID. Only revokes sessions owned by user_id."""
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.id == session_id,
                UserSession.user_id == user_id,
                UserSession.is_active == True,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            return False
        session.is_active = False
        session.revoked_at = datetime.now(timezone.utc)
        session.revoked_reason = reason
        await self.db.flush()
        return True

    async def revoke_all_sessions(self, user_id: uuid.UUID, reason: str = "sign_out_all") -> int:
        """Revoke all active sessions for a user. Returns count revoked."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
            )
        )
        sessions = result.scalars().all()
        for s in sessions:
            s.is_active = False
            s.revoked_at = now
            s.revoked_reason = reason
        await self.db.flush()
        return len(sessions)

    async def touch_session_by_token(self, token: str) -> bool:
        """Update last_seen_at for the session matching the token hash."""
        token_hash = _hash_token(token)
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.token_hash == token_hash,
                UserSession.is_active == True,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            return False
        session.last_seen_at = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    async def count_active_sessions(self, user_id: uuid.UUID) -> int:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > now,
            )
        )
        return len(result.scalars().all())
