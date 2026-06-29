"""Pydantic schemas for security, MFA, sessions, audit, GDPR, and SSO endpoints."""
import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ── MFA Schemas ────────────────────────────────────────────────────────────────
class MFAProvisionResponse(BaseModel):
    device_id: str
    secret: str
    otp_uri: str

class MFAVerifyRequest(BaseModel):
    device_id: uuid.UUID
    code: str = Field(..., min_length=6, max_length=8)

class MFAVerifyResponse(BaseModel):
    success: bool
    recovery_codes: list[str] = []
    error: Optional[str] = None

class MFAStatusResponse(BaseModel):
    enabled: bool
    method: Optional[str] = None
    device_name: Optional[str] = None
    last_used_at: Optional[str] = None

class MFACodeRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=8)

class RecoveryCodeCountResponse(BaseModel):
    remaining_count: int


# ── Session Schemas ────────────────────────────────────────────────────────────
class SessionResponse(BaseModel):
    id: str
    device_name: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    last_seen_at: str
    expires_at: str
    created_at: str

class SessionRevokeRequest(BaseModel):
    session_id: uuid.UUID
    reason: Optional[str] = "user_requested"


# ── Audit Schemas ──────────────────────────────────────────────────────────────
class AuditEventResponse(BaseModel):
    id: str
    event_type: str
    actor: str
    ip_address: Optional[str] = None
    risk_score: int
    metadata: dict = {}
    created_at: str

class AuditQueryParams(BaseModel):
    event_type: Optional[str] = None
    since_hours: int = 72
    limit: int = 100

class ComplianceReportResponse(BaseModel):
    workspace_id: str
    period_days: int
    high_risk_summary: dict
    events: list[AuditEventResponse]


# ── GDPR Schemas ───────────────────────────────────────────────────────────────
class DataExportResponse(BaseModel):
    export_id: str
    status: str
    download_url: Optional[str] = None
    expires_at: Optional[str] = None
    message: Optional[str] = None

class DeletionRequestCreate(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)

class DeletionStatusResponse(BaseModel):
    has_request: bool
    deletion_id: Optional[str] = None
    status: Optional[str] = None
    requested_at: Optional[str] = None
    scheduled_for: Optional[str] = None

class ConsentUpdate(BaseModel):
    consent_type: str = Field(..., max_length=100)
    granted: bool


# ── SSO Schemas ────────────────────────────────────────────────────────────────
class SSOConfigureRequest(BaseModel):
    provider: str = Field(..., pattern="^(google|microsoft|okta)$")
    client_id: str = Field(..., min_length=1)
    client_secret: str = Field(..., min_length=1)
    redirect_uri: str = Field(..., min_length=1)
    metadata: dict = Field(default_factory=dict)

class SSOConfigResponse(BaseModel):
    id: str
    provider: str
    client_id: str
    redirect_uri: str
    is_active: bool
    metadata: dict

class SSOAuthUrlResponse(BaseModel):
    provider: str
    authorization_url: str
    state: str


# ── Security Policy Schemas ────────────────────────────────────────────────────
class SecurityPolicyUpdate(BaseModel):
    mfa_required: Optional[bool] = None
    session_timeout_minutes: Optional[int] = Field(None, ge=15, le=10080)
    max_sessions_per_user: Optional[int] = Field(None, ge=1, le=20)
    ip_allowlist: Optional[list[str]] = None
    sso_required: Optional[bool] = None
    password_min_length: Optional[int] = Field(None, ge=6, le=128)
    password_require_special: Optional[bool] = None


# ── RBAC Schemas ───────────────────────────────────────────────────────────────
class RoleAssignRequest(BaseModel):
    target_user_id: uuid.UUID
    role: str = Field(..., pattern="^(VIEWER|COMMENTER|MEMBER|ADMIN|OWNER)$")

class RoleAssignResponse(BaseModel):
    success: bool
    old_role: Optional[str] = None
    new_role: Optional[str] = None
    error: Optional[str] = None

class MemberWithRoleResponse(BaseModel):
    user_id: str
    role: str
    permissions: list[str]
    joined_at: Optional[str] = None
