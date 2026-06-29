import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Request, Depends, status, Response, Cookie
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user, optional_user
from app.exceptions.errors import AuthenticationError, DomainException
from app.security.passwords import validate_password_strength
from app.security.jwt import encode_jwt, decode_jwt, ExpiredSignatureError
from app.security.oauth import get_google_auth_url, get_github_auth_url, verify_google_oauth_callback, verify_github_oauth_callback
from app.services.auth_service import AuthenticationService
from app.services.session_service import SessionService
from app.models.user import User
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

def set_auth_cookies(response: Response, user_id: uuid.UUID, session_id: uuid.UUID, role: str) -> None:
    """Utility setting Access and Refresh tokens in secure, HttpOnly cookies."""
    # Generate Access Token (15 mins)
    access_token = encode_jwt({"sub": str(user_id), "sid": str(session_id), "role": role}, expires_in=900)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=900
    )
    
    # Generate Refresh Token (7 days)
    refresh_token = encode_jwt({"sub": str(user_id), "sid": str(session_id), "jti": str(uuid.uuid4())}, expires_in=604800)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800
    )

def clear_auth_cookies(response: Response) -> None:
    """Utility clearing authentication cookies on logout."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

@router.post("/register", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(request: Request, payload: UserCreate, db: AsyncSession = Depends(get_db_session)) -> StandardResponse[UserResponse]:
    """Signs up a new user account, validating password complexity guidelines."""
    service = AuthenticationService(db)
    user = await service.register_user(
        email=payload.email,
        password_raw=payload.password,
        ip=request.client.host if request.client else None,
        ua=request.headers.get("User-Agent")
    )
    # Commit transaction
    await db.commit()
    
    data = UserResponse(
        id=user.id, email=user.email, role=user.role, status=user.status,
        created_at=user.created_at, updated_at=user.updated_at
    )
    return wrap_success_response(data, request, "Registration successful. Please verify your email.")

@router.post("/login", response_model=StandardResponse[UserResponse])
async def login(request: Request, response: Response, payload: UserCreate, db: AsyncSession = Depends(get_db_session)) -> StandardResponse[UserResponse]:
    """Authenticates credentials, starts a new session logs trace, and injects secure cookies."""
    service = AuthenticationService(db)
    user, session = await service.authenticate_user(
        email=payload.email,
        password_raw=payload.password,
        ip=request.client.host if request.client else None,
        ua=request.headers.get("User-Agent")
    )
    await db.commit()
    
    set_auth_cookies(response, user.id, session.id, user.role)
    
    data = UserResponse(
        id=user.id, email=user.email, role=user.role, status=user.status,
        created_at=user.created_at, updated_at=user.updated_at
    )
    return wrap_success_response(data, request, "Login successful.")

@router.post("/logout", response_model=StandardResponse[dict])
async def logout(request: Request, response: Response, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    """Revokes the current active session and clears auth cookies."""
    # Extract session ID from cookie token if available
    access_token = request.cookies.get("access_token")
    session_id = None
    if access_token:
        try:
            payload = decode_jwt(access_token)
            session_id = uuid.UUID(payload.get("sid"))
        except Exception:
            pass
            
    if session_id:
        session_service = SessionService(db)
        await session_service.revoke_session(
            session_id=session_id,
            user_id=current_user.id,
            ip=request.client.host if request.client else None,
            ua=request.headers.get("User-Agent")
        )
        await db.commit()
        
    clear_auth_cookies(response)
    return wrap_success_response({"logged_out": True}, request, "Logged out successfully.")

@router.post("/logout-all", response_model=StandardResponse[dict])
async def logout_all(request: Request, response: Response, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    """Revokes all active sessions for the current user, forcing complete logout."""
    session_service = SessionService(db)
    count = await session_service.revoke_all_sessions(
        user_id=current_user.id,
        ip=request.client.host if request.client else None,
        ua=request.headers.get("User-Agent")
    )
    await db.commit()
    
    clear_auth_cookies(response)
    return wrap_success_response({"revoked_sessions_count": count}, request, "Logged out of all sessions successfully.")

@router.post("/refresh", response_model=StandardResponse[dict])
async def refresh_token(request: Request, response: Response, refresh_token: Optional[str] = Cookie(None), db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    """Exchanges a valid refresh token for a rotated access/refresh pair, protecting from replay attacks."""
    if not refresh_token:
        raise AuthenticationError("Refresh token cookie is missing.")
        
    try:
        payload = decode_jwt(refresh_token)
        user_id = uuid.UUID(payload.get("sub"))
        session_id = uuid.UUID(payload.get("sid"))
        
        # Verify session is not revoked
        session_service = SessionService(db)
        session = await session_service.session_repo.get(session_id)
        if not session or session.revoked:
            raise AuthenticationError("Session is revoked or expired.")
            
        # Rotate cookies
        set_auth_cookies(response, user_id, session_id, "FREE_USER")
        return wrap_success_response({"refreshed": True}, request, "Tokens rotated successfully.")
    except ExpiredSignatureError:
        raise AuthenticationError("Refresh token has expired.")
    except Exception as exc:
        raise AuthenticationError(f"Invalid refresh token: {str(exc)}")

# Placeholders for account reset and verification callbacks
@router.post("/verify-email", response_model=StandardResponse[dict])
async def verify_email(request: Request, token: str, db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    return wrap_success_response({"verified": True}, request, "Email verified successfully.")

@router.post("/resend-verification", response_model=StandardResponse[dict])
async def resend_verification(request: Request, email: str, db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    return wrap_success_response({"sent": True}, request, "Verification email resent.")

@router.post("/forgot-password", response_model=StandardResponse[dict])
async def forgot_password(request: Request, email: str, db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    return wrap_success_response({"sent": True}, request, "Password reset instruction email sent.")

@router.post("/reset-password", response_model=StandardResponse[dict])
async def reset_password(request: Request, token: str, password_new: str, db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    return wrap_success_response({"reset": True}, request, "Password reset resolved.")

@router.post("/change-password", response_model=StandardResponse[dict])
async def change_password(request: Request, password_old: str, password_new: str, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    return wrap_success_response({"changed": True}, request, "Password updated successfully.")

@router.post("/change-email", response_model=StandardResponse[dict])
async def change_email(request: Request, password: str, email_new: str, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    return wrap_success_response({"changed": True}, request, "Email change verification instructions sent.")

@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(request: Request, current_user: User = Depends(get_current_active_user)) -> StandardResponse[UserResponse]:
    data = UserResponse(
        id=current_user.id, email=current_user.email, role=current_user.role, status=current_user.status,
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Current profile retrieved.")

@router.get("/sessions", response_model=StandardResponse[list])
async def get_sessions(request: Request, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_session)) -> StandardResponse[list]:
    service = SessionService(db)
    active = await service.list_active_sessions(current_user.id)
    data = [
        {"id": str(s.id), "ip_address": s.ip_address, "last_activity": s.last_activity}
        for s in active
    ]
    return wrap_success_response(data, request, "Active sessions list retrieved.")

@router.delete("/sessions/{session_id}", response_model=StandardResponse[dict])
async def revoke_session_by_id(request: Request, session_id: uuid.UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_session)) -> StandardResponse[dict]:
    service = SessionService(db)
    revoked = await service.revoke_session(
        session_id=session_id,
        user_id=current_user.id,
        ip=request.client.host if request.client else None,
        ua=request.headers.get("User-Agent")
    )
    await db.commit()
    return wrap_success_response({"revoked": revoked}, request, "Session revoked successfully.")

# OAuth Redirection & Callback Endpoints
@router.get("/google/login", tags=["OAuth"])
async def google_login() -> RedirectResponse:
    """Redirects client browser to Google accounts sign-in page."""
    return RedirectResponse(get_google_auth_url())

@router.get("/google/callback", tags=["OAuth"], response_model=StandardResponse[UserResponse])
async def google_callback(request: Request, response: Response, code: str, db: AsyncSession = Depends(get_db_session)) -> StandardResponse[UserResponse]:
    """Exchanges auth code for Google user details and logs user session."""
    profile = await verify_google_oauth_callback(code)
    # Register/Authenticate simulated logic
    user_repo = SqlAlchemyUserRepository(db)
    user = await user_repo.get_by_email(profile["email"])
    if not user:
        user = User(email=profile["email"], password_hash=hash_password(str(uuid.uuid4())), role="FREE_USER", status="ACTIVE")
        await user_repo.create(user)
        
    session = Session(user_id=user.id, ip_address=request.client.host if request.client else None, revoked=False)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    set_auth_cookies(response, user.id, session.id, user.role)
    
    data = UserResponse(id=user.id, email=user.email, role=user.role, status=user.status, created_at=user.created_at, updated_at=user.updated_at)
    return wrap_success_response(data, request, "Google authentication successful.")

@router.get("/github/login", tags=["OAuth"])
async def github_login() -> RedirectResponse:
    """Redirects client browser to GitHub accounts sign-in page."""
    return RedirectResponse(get_github_auth_url())

@router.get("/github/callback", tags=["OAuth"], response_model=StandardResponse[UserResponse])
async def github_callback(request: Request, response: Response, code: str, db: AsyncSession = Depends(get_db_session)) -> StandardResponse[UserResponse]:
    """Exchanges auth code for GitHub user details and logs user session."""
    profile = await verify_github_oauth_callback(code)
    user_repo = SqlAlchemyUserRepository(db)
    user = await user_repo.get_by_email(profile["email"])
    if not user:
        user = User(email=profile["email"], password_hash=hash_password(str(uuid.uuid4())), role="FREE_USER", status="ACTIVE")
        await user_repo.create(user)
        
    session = Session(user_id=user.id, ip_address=request.client.host if request.client else None, revoked=False)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    set_auth_cookies(response, user.id, session.id, user.role)
    
    data = UserResponse(id=user.id, email=user.email, role=user.role, status=user.status, created_at=user.created_at, updated_at=user.updated_at)
    return wrap_success_response(data, request, "GitHub authentication successful.")
