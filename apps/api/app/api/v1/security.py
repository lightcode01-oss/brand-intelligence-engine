"""Security API router: MFA, sessions, audit, GDPR, SSO, RBAC, and policy endpoints."""
import uuid
import secrets
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_user, get_current_workspace_id
from app.models.user import User
from app.schemas.security import (
    MFAProvisionResponse, MFAVerifyRequest, MFAVerifyResponse,
    MFAStatusResponse, MFACodeRequest, RecoveryCodeCountResponse,
    SessionResponse, SessionRevokeRequest,
    AuditEventResponse, ComplianceReportResponse,
    DataExportResponse, DeletionRequestCreate, DeletionStatusResponse,
    ConsentUpdate,
    SSOConfigureRequest, SSOConfigResponse, SSOAuthUrlResponse,
    SecurityPolicyUpdate,
    RoleAssignRequest, RoleAssignResponse, MemberWithRoleResponse,
)
from app.schemas.response import wrap_success_response, StandardResponse
from app.services.security import (
    MFAService, SessionManager, AuditService, RBACService, GDPRService, SSOService
)

router = APIRouter(prefix="/security", tags=["Security & Compliance"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MFA Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/mfa/status", response_model=StandardResponse[MFAStatusResponse])
async def mfa_status(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Return the current MFA enrollment status for the authenticated user."""
    svc = MFAService(db)
    status = await svc.get_device_status(current_user.id)
    return wrap_success_response(status, request, "MFA status retrieved.")


@router.post("/mfa/provision", response_model=StandardResponse[MFAProvisionResponse])
async def mfa_provision(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Provision a new TOTP MFA device and return the OTP URI for QR code generation."""
    svc = MFAService(db)
    result = await svc.provision_totp(current_user.id)
    await db.commit()
    return wrap_success_response(result, request, "TOTP device provisioned. Scan the QR code in your authenticator app.")


@router.post("/mfa/verify", response_model=StandardResponse[MFAVerifyResponse])
async def mfa_verify_setup(
    body: MFAVerifyRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Verify a TOTP code during initial setup and activate the MFA device."""
    svc = MFAService(db)
    audit = AuditService(db)
    result = await svc.verify_and_activate(current_user.id, body.device_id, body.code)
    event = "MFA_ENABLED" if result.get("success") else "MFA_FAILED"
    await audit.record(event, actor=str(current_user.email), user_id=current_user.id,
                       ip_address=request.client.host if request.client else None,
                       user_agent=request.headers.get("user-agent"))
    await db.commit()
    return wrap_success_response(result, request, "MFA activated successfully." if result.get("success") else "Verification failed.")


@router.delete("/mfa/disable", response_model=StandardResponse[dict])
async def mfa_disable(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Disable MFA for the authenticated user."""
    svc = MFAService(db)
    audit = AuditService(db)
    ok = await svc.disable_mfa(current_user.id)
    await audit.record("MFA_DISABLED", actor=str(current_user.email), user_id=current_user.id,
                       ip_address=request.client.host if request.client else None)
    await db.commit()
    return wrap_success_response({"disabled": ok}, request, "MFA disabled.")


@router.get("/mfa/recovery-codes", response_model=StandardResponse[RecoveryCodeCountResponse])
async def mfa_recovery_code_count(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Return the count of remaining valid recovery codes."""
    svc = MFAService(db)
    result = await svc.list_recovery_codes(current_user.id)
    return wrap_success_response(result, request)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Session Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/sessions", response_model=StandardResponse[list[SessionResponse]])
async def list_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Return all active sessions for the current user."""
    svc = SessionManager(db)
    sessions = await svc.get_active_sessions(current_user.id)
    return wrap_success_response(sessions, request, f"{len(sessions)} active session(s) found.")


@router.delete("/sessions/{session_id}", response_model=StandardResponse[dict])
async def revoke_session(
    session_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Revoke a specific session by ID."""
    svc = SessionManager(db)
    audit = AuditService(db)
    ok = await svc.revoke_session(session_id, current_user.id)
    if ok:
        await audit.record("SESSION_REVOKED", actor=str(current_user.email), user_id=current_user.id,
                           ip_address=request.client.host if request.client else None,
                           metadata={"session_id": str(session_id)})
    await db.commit()
    return wrap_success_response({"revoked": ok}, request, "Session revoked." if ok else "Session not found.")


@router.delete("/sessions", response_model=StandardResponse[dict])
async def revoke_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Revoke all active sessions for the current user (sign out everywhere)."""
    svc = SessionManager(db)
    audit = AuditService(db)
    count = await svc.revoke_all_sessions(current_user.id)
    await audit.record("SESSION_REVOKED", actor=str(current_user.email), user_id=current_user.id,
                       metadata={"revoked_count": count, "reason": "sign_out_all"})
    await db.commit()
    return wrap_success_response({"revoked_count": count}, request, f"{count} session(s) revoked.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Audit Log Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/audit", response_model=StandardResponse[list[AuditEventResponse]])
async def get_personal_audit_log(
    request: Request,
    event_type: str = Query(None),
    since_hours: int = Query(72, ge=1, le=8760),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Return the personal security audit log for the authenticated user."""
    svc = AuditService(db)
    events = await svc.query_events(
        user_id=current_user.id,
        event_type=event_type,
        since_hours=since_hours,
        limit=limit,
    )
    return wrap_success_response(events, request, f"{len(events)} audit event(s) returned.")


@router.get("/audit/workspace", response_model=StandardResponse[list[AuditEventResponse]])
async def get_workspace_audit_log(
    request: Request,
    event_type: str = Query(None),
    since_hours: int = Query(72, ge=1, le=8760),
    limit: int = Query(100, ge=1, le=500),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db_session),
):
    """Return the workspace-level security audit trail."""
    svc = AuditService(db)
    events = await svc.query_events(
        workspace_id=workspace_id,
        event_type=event_type,
        since_hours=since_hours,
        limit=limit,
    )
    return wrap_success_response(events, request, f"{len(events)} workspace audit event(s).")


@router.get("/audit/compliance", response_model=StandardResponse[dict])
async def get_compliance_report(
    request: Request,
    since_days: int = Query(30, ge=1, le=365),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db_session),
):
    """Generate a SOC 2 / compliance activity report for the workspace."""
    svc = AuditService(db)
    report = await svc.get_compliance_report(workspace_id, since_days)
    return wrap_success_response(report, request, "Compliance report generated.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GDPR Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/gdpr/export", response_model=StandardResponse[DataExportResponse])
async def request_data_export(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Submit a GDPR Article 20 data portability export request."""
    svc = GDPRService(db)
    audit = AuditService(db)
    result = await svc.request_data_export(current_user.id)
    await audit.record("DATA_EXPORT_REQUESTED", actor=str(current_user.email), user_id=current_user.id)
    await db.commit()
    return wrap_success_response(result, request, "Data export request submitted.")


@router.get("/gdpr/exports", response_model=StandardResponse[list[DataExportResponse]])
async def list_data_exports(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Return all data export requests for the authenticated user."""
    svc = GDPRService(db)
    exports = await svc.get_export_history(current_user.id)
    return wrap_success_response(exports, request)


@router.post("/gdpr/delete", response_model=StandardResponse[dict])
async def request_account_deletion(
    body: DeletionRequestCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Submit a GDPR Article 17 right-to-erasure deletion request."""
    svc = GDPRService(db)
    audit = AuditService(db)
    result = await svc.request_account_deletion(current_user.id, body.reason)
    await audit.record("DATA_DELETION_REQUESTED", actor=str(current_user.email), user_id=current_user.id,
                       metadata={"reason": body.reason})
    await db.commit()
    return wrap_success_response(result, request, "Account deletion request submitted.")


@router.delete("/gdpr/delete/cancel", response_model=StandardResponse[dict])
async def cancel_deletion_request(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Cancel a pending account deletion request."""
    svc = GDPRService(db)
    result = await svc.cancel_deletion_request(current_user.id)
    await db.commit()
    return wrap_success_response(result, request)


@router.get("/gdpr/delete/status", response_model=StandardResponse[DeletionStatusResponse])
async def deletion_status(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Check the deletion request status for the current user."""
    svc = GDPRService(db)
    status = await svc.get_deletion_status(current_user.id)
    return wrap_success_response(status, request)


@router.post("/gdpr/consent", response_model=StandardResponse[dict])
async def update_consent(
    body: ConsentUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Record a user consent decision."""
    svc = GDPRService(db)
    result = await svc.record_consent(
        user_id=current_user.id,
        consent_type=body.consent_type,
        granted=body.granted,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()
    return wrap_success_response(result, request, "Consent preference recorded.")


@router.get("/gdpr/consent", response_model=StandardResponse[list[dict]])
async def get_consent_history(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Return the full consent history for the authenticated user."""
    svc = GDPRService(db)
    records = await svc.get_consent_history(current_user.id)
    return wrap_success_response(records, request)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SSO Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/sso/providers", response_model=StandardResponse[list[str]])
async def list_sso_providers(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Return the list of supported SSO provider names."""
    svc = SSOService(db)
    return wrap_success_response(svc.get_available_providers(), request)


@router.get("/sso/config", response_model=StandardResponse[dict])
async def get_sso_config(
    request: Request,
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db_session),
):
    """Return the current SSO configuration for the workspace."""
    svc = SSOService(db)
    config = await svc.get_sso_config(workspace_id)
    return wrap_success_response(config or {}, request, "SSO configuration retrieved.")


@router.post("/sso/configure", response_model=StandardResponse[dict])
async def configure_sso(
    body: SSOConfigureRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db_session),
):
    """Create or update SSO provider configuration for the workspace."""
    svc = SSOService(db)
    result = await svc.configure_sso(
        workspace_id=workspace_id,
        provider=body.provider,
        client_id=body.client_id,
        client_secret=body.client_secret,
        redirect_uri=body.redirect_uri,
        metadata=body.metadata,
    )
    await db.commit()
    return wrap_success_response(result, request, "SSO configuration saved.")


@router.get("/sso/authorize/{provider}", response_model=StandardResponse[SSOAuthUrlResponse])
async def get_sso_auth_url(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """Generate an OAuth2 authorization URL for the given SSO provider."""
    svc = SSOService(db)
    state = secrets.token_urlsafe(32)
    provider_map = {
        "google": lambda: __import__("app.services.security.sso", fromlist=["GoogleSSO"]).GoogleSSO("", ""),
        "microsoft": lambda: __import__("app.services.security.sso", fromlist=["MicrosoftSSO"]).MicrosoftSSO("", ""),
        "okta": lambda: __import__("app.services.security.sso", fromlist=["OktaSSO"]).OktaSSO("", "", "example.okta.com"),
    }
    if provider not in provider_map:
        return wrap_success_response({"error": "Unknown provider"}, request)

    p = provider_map[provider]()
    auth_url = p.get_authorization_url(redirect_uri="https://nomen.ai/auth/callback", state=state)
    return wrap_success_response(
        {"provider": provider, "authorization_url": auth_url, "state": state},
        request,
        "Authorization URL generated."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RBAC Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/rbac/members", response_model=StandardResponse[list[MemberWithRoleResponse]])
async def list_members_rbac(
    request: Request,
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db_session),
):
    """List all workspace members with their roles and effective permissions."""
    svc = RBACService(db)
    members = await svc.list_members_with_roles(workspace_id)
    return wrap_success_response(members, request, f"{len(members)} member(s) found.")


@router.post("/rbac/assign", response_model=StandardResponse[RoleAssignResponse])
async def assign_role(
    body: RoleAssignRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db_session),
):
    """Assign a new workspace role to a member (requires roles.assign permission)."""
    svc = RBACService(db)
    audit = AuditService(db)
    result = await svc.assign_role(
        workspace_id=workspace_id,
        target_user_id=body.target_user_id,
        new_role=body.role,
        assigning_user_id=current_user.id,
    )
    if result.get("success"):
        await audit.record("ROLE_CHANGED", actor=str(current_user.email), user_id=current_user.id,
                           workspace_id=workspace_id,
                           metadata={"target_user_id": str(body.target_user_id),
                                     "old_role": result.get("old_role"),
                                     "new_role": result.get("new_role")})
    await db.commit()
    return wrap_success_response(result, request)


@router.get("/rbac/roles", response_model=StandardResponse[list[dict]])
async def list_roles(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Return all available RBAC roles and their permission sets."""
    svc = RBACService(db)
    return wrap_success_response(svc.get_all_roles(), request)
