from typing import List, Callable
from fastapi import Request, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.exceptions.errors import AuthenticationError, AuthorizationError
from app.services.billing.api_key_service import APIKeyService

def require_api_key(required_scopes: List[str]) -> Callable:
    """Dependency checking that requests hold valid API keys containing required scopes."""
    async def api_key_checker(
        request: Request,
        authorization: str = Header(...),
        db: AsyncSession = Depends(get_db_session)
    ) -> None:
        if not authorization.startswith("Bearer "):
            raise AuthenticationError("Authorization header must use Bearer scheme.")
            
        raw_key = authorization.split(" ")[1]
        service = APIKeyService(db)
        key_record = await service.authenticate_key(raw_key)
        
        # Verify scopes presence
        assigned_scopes = key_record.scopes_json.get("scopes", [])
        for scope in required_scopes:
            if scope not in assigned_scopes:
                raise AuthorizationError(f"Missing required API key scope: {scope}")
                
        # Set context variables on request state
        request.state.user_id = key_record.user_id
        
    return api_key_checker
