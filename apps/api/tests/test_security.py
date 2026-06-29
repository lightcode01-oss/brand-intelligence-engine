import pytest
import uuid
import time
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.exceptions.errors import AuthenticationError, AuthorizationError, DomainException
from app.security.passwords import hash_password, verify_password, validate_password_strength
from app.security.jwt import encode_jwt, decode_jwt, ExpiredSignatureError, JWTError
from app.services.auth_service import AuthenticationService
from app.services.session_service import SessionService
from app.services.permission_service import PermissionService
from app.models.user import User, Session, Role, Permission
from app.models.workspace import WorkspaceMember

@pytest.mark.asyncio
async def test_password_hashing_and_complexity() -> None:
    # 1. Complexity constraints
    ok, errors = validate_password_strength("weak")
    assert ok is False
    assert len(errors) > 0
    
    ok, errors = validate_password_strength("SecurePass123!")
    assert ok is True
    assert len(errors) == 0
    
    # 2. Hash and verify
    raw = "ComplexP@ssw0rd!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong_password", hashed) is False

@pytest.mark.asyncio
async def test_jwt_generation_and_decoding() -> None:
    payload = {"sub": "user_uuid_123", "role": "FREE_USER"}
    token = encode_jwt(payload, expires_in=10)
    assert token is not None
    
    decoded = decode_jwt(token)
    assert decoded["sub"] == "user_uuid_123"
    assert decoded["role"] == "FREE_USER"
    
    # Expiry test
    expired_token = encode_jwt(payload, expires_in=-10)
    with pytest.raises(ExpiredSignatureError):
        decode_jwt(expired_token)

@pytest.mark.asyncio
async def test_account_lockout_workflow(db_session: AsyncSession) -> None:
    service = AuthenticationService(db_session)
    email = "lockout@nomen.ai"
    password = "SecurePassword123!"
    
    # 1. Register
    user = await service.register_user(email, password)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Enable active status
    user.status = "ACTIVE"
    await db_session.commit()
    
    # 2. Trigger 5 failed login attempts
    for _ in range(5):
        with pytest.raises(AuthenticationError):
            await service.authenticate_user(email, "incorrect_password")
            
    # Verify user lockout status
    await db_session.refresh(user)
    assert user.failed_login_count == 5
    assert user.locked_until is not None
    locked_until = user.locked_until
    now = datetime.now(timezone.utc)
    if locked_until.tzinfo is None:
        now = now.replace(tzinfo=None)
    assert locked_until > now
    
    # Attempting to login in locked state fails
    with pytest.raises(AuthenticationError) as exc_info:
        await service.authenticate_user(email, password)
    assert "consecutive failures" in str(exc_info.value)

@pytest.mark.asyncio
async def test_session_lifecycle(db_session: AsyncSession) -> None:
    auth_service = AuthenticationService(db_session)
    session_service = SessionService(db_session)
    
    email = "session@nomen.ai"
    password = "SecurePassword123!"
    user = await auth_service.register_user(email, password)
    user.status = "ACTIVE"
    await db_session.commit()
    
    # 1. Login sets active session
    user, session = await auth_service.authenticate_user(email, password)
    await db_session.commit()
    
    active = await session_service.list_active_sessions(user.id)
    assert len(active) == 1
    assert active[0].id == session.id
    
    # 2. Revoke session
    revoked = await session_service.revoke_session(session.id, user.id)
    await db_session.commit()
    assert revoked is True
    
    # Verify session marked revoked
    active_after = await session_service.list_active_sessions(user.id)
    assert len(active_after) == 0

@pytest.mark.asyncio
async def test_rbac_permission_matching(db_session: AsyncSession) -> None:
    perm_service = PermissionService(db_session)
    
    # Create User and Workspace Membership
    user = User(email="member@nomen.ai", password_hash="hashed_pw", role="FREE_USER", status="ACTIVE")
    db_session.add(user)
    await db_session.flush()
    
    workspace_id = uuid.uuid4()
    membership = WorkspaceMember(workspace_id=workspace_id, user_id=user.id, role="member")
    db_session.add(membership)
    await db_session.commit()
    
    # Member role permissions check
    assert await perm_service.check_workspace_permission(workspace_id, user.id, "project.read") is True
    assert await perm_service.check_workspace_permission(workspace_id, user.id, "project.write") is True
    assert await perm_service.check_workspace_permission(workspace_id, user.id, "workspace.delete") is False # Viewer/Member cannot delete workspace
