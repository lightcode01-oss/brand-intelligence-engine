import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Enum, ForeignKey, Boolean, Integer, DateTime, Table, Column, func, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, StandardBase, ImmutableBase

# Custom ENUM types
user_role_enum = Enum("GUEST", "FREE_USER", "PRO_USER", "ADMIN", "SUPER_ADMIN", name="user_role")
user_status_enum = Enum("PENDING_ACTIVATION", "ACTIVE", "SUSPENDED", name="user_status")
subscription_tier_enum = Enum("FREE", "PRO", "ENTERPRISE", name="subscription_tier")
subscription_status_enum = Enum("ACTIVE", "PAST_DUE", "CANCELED", name="subscription_status")
credit_txn_type_enum = Enum("CREDIT", "DEBIT", "REFUND", name="credit_transaction_type")
invoice_status_enum = Enum("PAID", "OPEN", "VOID", name="invoice_status")
notification_type_enum = Enum("EMAIL", "IN_APP", "WEBHOOK", name="notification_type")

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

class Plan(StandardBase):
    """SaaS pricing tier metrics and flags limits config."""
    __tablename__ = "plans"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    price_monthly: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    limits_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    features_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

class Subscription(StandardBase):
    __tablename__ = "subscriptions"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    tier: Mapped[str] = mapped_column(subscription_tier_enum, default="FREE", nullable=False)
    status: Mapped[str] = mapped_column(subscription_status_enum, default="ACTIVE", nullable=False)
    limit_reset_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    monthly_query_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

class Invoice(StandardBase):
    """Payment ledger record track."""
    __tablename__ = "invoices"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(invoice_status_enum, default="OPEN", nullable=False)
    billing_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

class CreditTransaction(StandardBase):
    """Credit logs track for generation quotas."""
    __tablename__ = "credit_transactions"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(credit_txn_type_enum, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class UsageRecord(StandardBase):
    """Tracks consumption counts per workspace and user."""
    __tablename__ = "usage_records"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "generation", "export"
    count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class APIKey(StandardBase):
    """API Key tokens configuration for developers."""
    __tablename__ = "api_keys"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    hashed_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scopes_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class Notification(StandardBase):
    """System-level and email notifications records."""
    __tablename__ = "notifications"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    type: Mapped[str] = mapped_column(notification_type_enum, default="IN_APP", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class Coupon(StandardBase):
    """Promo discounts settings."""
    __tablename__ = "coupons"
    
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    discount_percent: Mapped[float] = mapped_column(Float, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class WebhookEvent(StandardBase):
    """Raw payload logs registry from external payment portals."""
    __tablename__ = "webhook_events"
    
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

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
