import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Enum, ForeignKey, Boolean, Integer, DateTime, Table, Column, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, StandardBase, ImmutableBase

# Custom ENUM types
user_role_enum = Enum("GUEST", "FREE_USER", "PRO_USER", "ADMIN", name="user_role")
user_status_enum = Enum("PENDING_ACTIVATION", "ACTIVE", "SUSPENDED", name="user_status")
subscription_tier_enum = Enum("FREE", "PRO", "ENTERPRISE", name="subscription_tier")
subscription_status_enum = Enum("ACTIVE", "PAST_DUE", "CANCELED", name="subscription_status")

# Association Table for Role and Permission (Many-to-Many)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="RESTRICT"), primary_key=True)
)

# Association Table for User and Role (Many-to-Many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True)
)

class Permission(StandardBase):
    __tablename__ = "permissions"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class Role(StandardBase):
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    permissions: Mapped[List[Permission]] = relationship(
        "Permission",
        secondary=role_permissions,
        lazy="selectin"
    )

class User(StandardBase):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(user_role_enum, default="FREE_USER", nullable=False)
    status: Mapped[str] = mapped_column(user_status_enum, default="ACTIVE", nullable=False)
    
    # Account Lockout fields
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    roles: Mapped[List[Role]] = relationship(
        "Role",
        secondary=user_roles,
        lazy="selectin"
    )

class WorkspaceRole(StandardBase):
    """Workspace-level membership Role assignment."""
    __tablename__ = "workspace_roles"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    
    role: Mapped[Role] = relationship("Role", lazy="selectin")

class Subscription(StandardBase):
    __tablename__ = "subscriptions"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    tier: Mapped[str] = mapped_column(subscription_tier_enum, default="FREE", nullable=False)
    status: Mapped[str] = mapped_column(subscription_status_enum, default="ACTIVE", nullable=False)
    limit_reset_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    monthly_query_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

class Session(StandardBase):
    """Tracks active authenticated user sessions."""
    __tablename__ = "sessions"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    device: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    last_activity: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class RefreshToken(StandardBase):
    """Tracks rotated refresh tokens and correlation chains."""
    __tablename__ = "refresh_tokens"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id", ondelete="RESTRICT"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    jti: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class VerificationToken(StandardBase):
    """One-time token for account email confirmation."""
    __tablename__ = "verification_tokens"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class PasswordResetToken(StandardBase):
    """One-time token for secure password resets."""
    __tablename__ = "password_reset_tokens"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class AuditLog(ImmutableBase):
    __tablename__ = "audit_logs"
    
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    entity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

class FeatureFlag(StandardBase):
    __tablename__ = "feature_flags"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
