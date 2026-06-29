import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.errors import AuthenticationError, RateLimitError, DomainException
from app.security.passwords import hash_password, verify_password, validate_password_strength
from app.security.jwt import encode_jwt
from app.repositories.auth import SqlAlchemyUserRepository, SqlAlchemySessionRepository, SqlAlchemyVerificationTokenRepository, SqlAlchemyPasswordResetTokenRepository, SqlAlchemyAuditLogRepository
from app.models.user import User, Session, VerificationToken, PasswordResetToken, AuditLog

class AuthenticationService:
    """Core Authentication & Account security workflows manager."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = SqlAlchemyUserRepository(db)
        self.session_repo = SqlAlchemySessionRepository(db)
        self.verification_repo = SqlAlchemyVerificationTokenRepository(db)
        self.reset_repo = SqlAlchemyPasswordResetTokenRepository(db)
        self.audit_repo = SqlAlchemyAuditLogRepository(db)
        
    async def register_user(self, email: str, password_raw: str, ip: str = None, ua: str = None) -> User:
        """Registers a new user and logs an audit trail event."""
        # 1. Check if email unique
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise DomainException("Email address is already registered.")
            
        # 2. Check password complexity
        ok, errors = validate_password_strength(password_raw)
        if not ok:
            raise DomainException("Password fails complexity checks.", errors=errors)
            
        # 3. Create user
        new_user = User(
            email=email.strip().lower(),
            password_hash=hash_password(password_raw),
            role="FREE_USER",
            status="PENDING_ACTIVATION"
        )
        await self.user_repo.create(new_user)
        
        # 4. Generate audit event
        audit = AuditLog(
            actor=email,
            entity_name="User",
            entity_id=new_user.id,
            action="USER_REGISTERED",
            ip_address=ip,
            user_agent=ua
        )
        await self.audit_repo.create(audit)
        
        return new_user

    async def authenticate_user(self, email: str, password_raw: str, ip: str = None, ua: str = None) -> Tuple[User, Session]:
        """Authenticates credentials, manages brute force lockout state, and initializes session logs."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password.")
            
        # 1. Lockout verification check
        now = datetime.now(timezone.utc)
        if user.locked_until:
            locked_until = user.locked_until
            comp_now = now if locked_until.tzinfo is not None else now.replace(tzinfo=None)
            if locked_until > comp_now:
                minutes_left = int((locked_until - comp_now).total_seconds() / 60) + 1
                raise AuthenticationError(f"Account locked due to consecutive failures. Please wait {minutes_left} minutes.")
            
        # 2. Verify password credentials
        if not verify_password(password_raw, user.password_hash):
            # Increment failed attempts
            user.failed_login_count += 1
            if user.failed_login_count >= 5:
                user.locked_until = now + timedelta(minutes=15)
                # Log audit lockout
                await self.audit_repo.create(AuditLog(
                    actor=email, entity_name="User", entity_id=user.id,
                    action="ACCOUNT_LOCKED", ip_address=ip, user_agent=ua
                ))
            await self.user_repo.update(user)
            raise AuthenticationError("Invalid email or password.")
            
        # 3. Reset failed login counter on success
        user.failed_login_count = 0
        user.locked_until = None
        await self.user_repo.update(user)
        
        # 4. Create session
        session = Session(
            user_id=user.id,
            device=None, # Parsed later from User-Agent
            browser=None,
            os=None,
            ip_address=ip,
            revoked=False
        )
        await self.session_repo.create(session)
        
        # 5. Log audit login success
        await self.audit_repo.create(AuditLog(
            actor=str(user.id), entity_name="User", entity_id=user.id,
            action="USER_LOGIN_SUCCESS", ip_address=ip, user_agent=ua
        ))
        
        return user, session
