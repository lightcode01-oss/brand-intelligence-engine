import uuid
from typing import Optional, Callable
from fastapi import Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.exceptions.errors import AuthenticationError, AuthorizationError
from app.security.jwt import decode_jwt, ExpiredSignatureError
from app.repositories.auth import SqlAlchemyUserRepository, SqlAlchemySessionRepository
from app.models.user import User
from app.services.permission_service import PermissionService

async def optional_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """Dependency retrieving the authenticated user if valid auth headers exist, otherwise returning None."""
    # Check authorization cookie fallback
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    else:
        token = request.cookies.get("access_token")
        
    if not token:
        return None
        
    try:
        payload = decode_jwt(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
            
        user_id = uuid.UUID(user_id_str)
        user_repo = SqlAlchemyUserRepository(db)
        user = await user_repo.get(user_id)
        
        # Check active status
        if not user or user.status != "ACTIVE":
            return None
            
        # Bind user metadata to request context
        request.state.user_id = user.id
        return user
    except Exception:
        return None

async def get_current_user(user: Optional[User] = Depends(optional_user)) -> User:
    """Dependency requiring valid authentication credentials, raising 401 if invalid."""
    if not user:
        raise AuthenticationError("Authorization token is missing, invalid, or expired.")
    return user

def require_role(allowed_roles: list[str]) -> Callable:
    """Dependency factory checking that the authenticated user holds an authorized global role."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and current_user.role != "SUPER_ADMIN":
            raise AuthorizationError("Your global role is unauthorized to execute this action.")
        return current_user
    return role_checker

async def get_current_workspace_id(request: Request) -> uuid.UUID:
    """Dependency extracting the active workspace ID from route parameters or headers."""
    # Try route parameter first
    workspace_id_str = request.path_params.get("workspace_id")
    if not workspace_id_str:
        # Check headers
        workspace_id_str = request.headers.get("X-Workspace-Id")
        
    if not workspace_id_str:
        raise AuthorizationError("Active workspace context header or ID parameter is missing.")
        
    try:
        workspace_id = uuid.UUID(workspace_id_str)
        request.state.workspace_id = workspace_id
        return workspace_id
    except ValueError:
        raise AuthorizationError("Invalid workspace ID format.")

def require_permission(permission_name: str) -> Callable:
    """Dependency factory verifying that the user has workspace-level authorization for the action."""
    async def permission_checker(
        workspace_id: uuid.UUID = Depends(get_current_workspace_id),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session)
    ) -> User:
        service = PermissionService(db)
        authorized = await service.check_workspace_permission(workspace_id, current_user.id, permission_name)
        if not authorized:
            raise AuthorizationError(f"You do not possess the required workspace permission: {permission_name}")
        return current_user
    return permission_checker

async def require_workspace_owner(
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Dependency verifying that the user is the explicit owner of the workspace context."""
    service = PermissionService(db)
    authorized = await service.check_workspace_permission(workspace_id, current_user.id, "workspace.delete")
    if not authorized:
        raise AuthorizationError("Only workspace owners can perform this operation.")
    return current_user
