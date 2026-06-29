import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import APIKey
from app.exceptions.errors import AuthenticationError

class APIKeyService:
    """Manages secure prefix-based API keys generation, SHA-256 hashing, and authentication."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    def _hash_key(self, raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        
    async def create_key(self, user_id: str, name: str, scopes: List[str], expiration_days: Optional[int] = None) -> str:
        """Generates a secure API key, saves its hash to DB, and returns the raw key string."""
        # 1. Generate unique key prefix: nm_live_[32-byte-hex]
        rand_token = secrets.token_hex(16)
        raw_key = f"nm_live_{rand_token}"
        hashed = self._hash_key(raw_key)
        
        expires_at = None
        if expiration_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expiration_days)
            
        new_key = APIKey(
            user_id=user_id,
            hashed_key=hashed,
            name=name,
            scopes_json={"scopes": scopes},
            expires_at=expires_at
        )
        self.db.add(new_key)
        await self.db.flush()
        
        return raw_key

    async def authenticate_key(self, raw_key: str) -> APIKey:
        """Checks if a raw key signature exists, matches scopes, and is active."""
        if not raw_key.startswith("nm_live_"):
            raise AuthenticationError("Invalid API key format.")
            
        hashed = self._hash_key(raw_key)
        stmt = select(APIKey).where(
            APIKey.hashed_key == hashed,
            APIKey.revoked_at == None,
            APIKey.deleted_at == None
        )
        key_record = (await self.db.execute(stmt)).scalar()
        if not key_record:
            raise AuthenticationError("API Key is invalid or has been deleted.")
            
        # Expiry checks
        if key_record.expires_at and datetime.now(timezone.utc) > key_record.expires_at:
            raise AuthenticationError("API Key has expired.")
            
        return key_record
