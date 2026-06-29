import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, StandardBase, ImmutableBase

# Enum definitions
security_event_type_enum = Enum(
    "LOGIN_SUCCESS", "LOGIN_FAILED", "LOGOUT", "PASSWORD_CHANGED", "PASSWORD_RESET",
    "MFA_ENABLED", "MFA_DISABLED", "MFA_VERIFIED", "MFA_FAILED",
    "SESSION_REVOKED", "API_KEY_CREATED", "API_KEY_REVOKED",
    "ROLE_CHANGED", "EXPORT_REQUESTED", "EXPORT_COMPLETED",
    "ACCOUNT_LOCKED", "ACCOUNT_UNLOCKED", "SSO_LOGIN",
    "DATA_EXPORT_REQUESTED", "DATA_DELETION_REQUESTED",
    name="security_event_type"
)

mfa_method_enum = Enum("TOTP", "RECOVERY_CODE", name="mfa_method")

class UserSession(StandardBase):
    """Tracks detailed authenticated user sessions including device fingerprinting."""
    __tablename__ = "user_sessions"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    device_fingerprint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    device_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class MFADevice(StandardBase):
    """Stores TOTP MFA device registrations for users."""
    __tablename__ = "mfa_devices"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    method: Mapped[str] = mapped_column(mfa_method_enum, default="TOTP", nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Authenticator App")
    secret_encrypted: Mapped[str] = mapped_column(Text, nullable=False)  # encrypted TOTP secret
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    backup_codes_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class RecoveryCode(ImmutableBase):
    """Single-use backup codes generated alongside MFA activation."""
    __tablename__ = "recovery_codes"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    mfa_device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mfa_devices.id", ondelete="CASCADE"), nullable=False)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class SecurityEvent(ImmutableBase):
    """Immutable audit trail for all security-relevant platform events."""
    __tablename__ = "security_events"
    
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[str] = mapped_column(security_event_type_enum, nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)  # email or system
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0–100

class SecurityPolicy(StandardBase):
    """Configurable workspace-level security policies."""
    __tablename__ = "security_policies"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True
    )
    mfa_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    session_timeout_minutes: Mapped[int] = mapped_column(Integer, default=480, nullable=False)  # 8 hours
    max_sessions_per_user: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    ip_allowlist: Mapped[dict] = mapped_column(JSONB, default=list, nullable=False)  # list of CIDR strings
    sso_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sso_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "google", "microsoft", "okta"
    password_min_length: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    password_require_special: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class SSOProvider(StandardBase):
    """SSO provider configurations per workspace."""
    __tablename__ = "sso_providers"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # "google", "microsoft", "okta"
    client_id: Mapped[str] = mapped_column(String(255), nullable=False)
    client_secret_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    redirect_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)  # issuer, etc.

class DataExportRequest(StandardBase):
    """GDPR Article 20 — user data portability export requests."""
    __tablename__ = "data_export_requests"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, PROCESSING, COMPLETED, FAILED
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    download_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class DataDeletionRequest(StandardBase):
    """GDPR Article 17 — right to erasure deletion requests."""
    __tablename__ = "data_deletion_requests"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, CONFIRMED, PROCESSING, COMPLETED
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # 30-day grace period

class ConsentRecord(ImmutableBase):
    """Tracks user consent events for GDPR compliance."""
    __tablename__ = "consent_records"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    consent_type: Mapped[str] = mapped_column(String(100), nullable=False)  # "marketing", "analytics", "necessary"
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
