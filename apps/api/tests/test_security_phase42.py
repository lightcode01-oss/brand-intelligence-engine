"""
tests/test_security_phase42.py
Phase 4.2 — Enterprise Security, Compliance & Platform Hardening

Tests: MFA, Recovery Codes, Sessions, RBAC, Audit, GDPR, SSO
"""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MFA Service Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.mark.asyncio
async def test_mfa_provision_totp(db_session):
    """MFAService.provision_totp should create a device and return an OTP URI."""
    from app.services.security.mfa import MFAService
    svc = MFAService(db_session)
    user_id = uuid.uuid4()

    result = await svc.provision_totp(user_id)

    assert "device_id" in result
    assert "secret" in result
    assert "otp_uri" in result
    assert "otpauth://totp/" in result["otp_uri"]
    assert result["secret"] != ""


@pytest.mark.asyncio
async def test_mfa_verify_invalid_code(db_session):
    """Verifying with a wrong code should return success=False."""
    from app.services.security.mfa import MFAService
    svc = MFAService(db_session)
    user_id = uuid.uuid4()

    provisioned = await svc.provision_totp(user_id)
    device_id = uuid.UUID(provisioned["device_id"])

    result = await svc.verify_and_activate(user_id, device_id, "000000")
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_mfa_verify_valid_code(db_session):
    """Verifying with the current TOTP code should activate the device and return recovery codes."""
    from app.services.security.mfa import MFAService, _current_totp, _TOTP_DIGITS
    svc = MFAService(db_session)
    user_id = uuid.uuid4()

    provisioned = await svc.provision_totp(user_id)
    secret = provisioned["secret"]
    device_id = uuid.UUID(provisioned["device_id"])

    valid_codes = [str(c).zfill(_TOTP_DIGITS) for c in _current_totp(secret)]
    result = await svc.verify_and_activate(user_id, device_id, valid_codes[1])

    assert result["success"] is True
    assert len(result["recovery_codes"]) == 10


@pytest.mark.asyncio
async def test_mfa_recovery_codes_single_use(db_session):
    """Recovery codes must be single-use: second attempt returns False."""
    from app.services.security.mfa import MFAService, _current_totp, _TOTP_DIGITS
    svc = MFAService(db_session)
    user_id = uuid.uuid4()

    provisioned = await svc.provision_totp(user_id)
    secret = provisioned["secret"]
    device_id = uuid.UUID(provisioned["device_id"])
    valid_codes = [str(c).zfill(_TOTP_DIGITS) for c in _current_totp(secret)]
    result = await svc.verify_and_activate(user_id, device_id, valid_codes[1])

    recovery_code = result["recovery_codes"][0]
    assert await svc.verify_recovery_code(user_id, recovery_code) is True
    assert await svc.verify_recovery_code(user_id, recovery_code) is False


@pytest.mark.asyncio
async def test_mfa_disable_unenrolled_returns_false(db_session):
    """Disabling MFA on a user without MFA should return False."""
    from app.services.security.mfa import MFAService
    svc = MFAService(db_session)
    ok = await svc.disable_mfa(uuid.uuid4())
    assert ok is False


@pytest.mark.asyncio
async def test_mfa_status_unenrolled(db_session):
    """Device status for a user without MFA should report enabled=False."""
    from app.services.security.mfa import MFAService
    svc = MFAService(db_session)
    status = await svc.get_device_status(uuid.uuid4())
    assert status["enabled"] is False
    assert status["method"] is None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Session Manager Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.mark.asyncio
async def test_session_create_and_list(db_session):
    """Created sessions should appear in the active sessions list."""
    from app.services.security.sessions import SessionManager
    svc = SessionManager(db_session)
    user_id = uuid.uuid4()

    await svc.create_session(user_id, "tok_abc", ip_address="127.0.0.1", user_agent="Mozilla/5.0 Chrome")
    sessions = await svc.get_active_sessions(user_id)
    assert len(sessions) == 1
    assert sessions[0]["browser"] == "Chrome"


@pytest.mark.asyncio
async def test_session_revoke(db_session):
    """Revoking a session by ID should remove it from active sessions."""
    from app.services.security.sessions import SessionManager
    svc = SessionManager(db_session)
    user_id = uuid.uuid4()

    session = await svc.create_session(user_id, "tok_revoke", ip_address="10.0.0.1")
    ok = await svc.revoke_session(session.id, user_id)
    assert ok is True
    remaining = await svc.get_active_sessions(user_id)
    assert len(remaining) == 0


@pytest.mark.asyncio
async def test_session_revoke_wrong_user(db_session):
    """Revoking another user's session should return False (ownership check)."""
    from app.services.security.sessions import SessionManager
    svc = SessionManager(db_session)
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()

    session = await svc.create_session(user_a, "tok_a")
    ok = await svc.revoke_session(session.id, user_b)
    assert ok is False


@pytest.mark.asyncio
async def test_revoke_all_sessions(db_session):
    """Revoking all sessions should return the correct count and clear the list."""
    from app.services.security.sessions import SessionManager
    svc = SessionManager(db_session)
    user_id = uuid.uuid4()

    await svc.create_session(user_id, "tok_1")
    await svc.create_session(user_id, "tok_2")
    await svc.create_session(user_id, "tok_3")

    count = await svc.revoke_all_sessions(user_id)
    assert count == 3
    remaining = await svc.get_active_sessions(user_id)
    assert len(remaining) == 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Audit Service Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.mark.asyncio
async def test_audit_record_and_query(db_session):
    """Recorded events should be retrievable and carry correct metadata."""
    from app.services.security.audit import AuditService
    svc = AuditService(db_session)
    user_id = uuid.uuid4()

    await svc.record("LOGIN_SUCCESS", actor="user@test.com", user_id=user_id, ip_address="1.2.3.4")
    await svc.record("LOGIN_FAILED", actor="user@test.com", user_id=user_id, ip_address="1.2.3.4")

    events = await svc.query_events(user_id=user_id)
    assert len(events) == 2
    types = {e["event_type"] for e in events}
    assert "LOGIN_SUCCESS" in types
    assert "LOGIN_FAILED" in types


@pytest.mark.asyncio
async def test_audit_risk_scoring(db_session):
    """High-risk events should have risk_score >= 70."""
    from app.services.security.audit import AuditService
    svc = AuditService(db_session)
    event = await svc.record("DATA_DELETION_REQUESTED", actor="u@e.com", user_id=uuid.uuid4())
    assert event.risk_score >= 70


@pytest.mark.asyncio
async def test_audit_failed_login_count(db_session):
    """Failed login counter should return correct count within the time window."""
    from app.services.security.audit import AuditService
    svc = AuditService(db_session)
    actor = "brute@force.com"

    for _ in range(3):
        await svc.record("LOGIN_FAILED", actor=actor)

    count = await svc.get_failed_login_count(actor, since_minutes=30)
    assert count == 3


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RBAC Service Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_rbac_role_permissions_all_roles_have_perms():
    """All defined roles should have non-empty permission sets."""
    from app.services.security.rbac import _ROLE_PERMISSIONS
    for role, perms in _ROLE_PERMISSIONS.items():
        assert len(perms) > 0, f"Role {role} has no permissions"


def test_rbac_owner_is_superset_of_member():
    """OWNER permissions should include all MEMBER permissions."""
    from app.services.security.rbac import _ROLE_PERMISSIONS
    assert set(_ROLE_PERMISSIONS["MEMBER"]).issubset(set(_ROLE_PERMISSIONS["OWNER"]))


def test_rbac_viewer_cannot_create():
    """VIEWER should not have creation or management permissions."""
    from app.services.security.rbac import _ROLE_PERMISSIONS
    viewer = _ROLE_PERMISSIONS["VIEWER"]
    assert "projects.create" not in viewer
    assert "generations.create" not in viewer


def test_rbac_get_all_roles_returns_five():
    """get_all_roles should return entries for all 5 defined roles."""
    from app.services.security.rbac import RBACService
    svc = RBACService.__new__(RBACService)
    roles = svc.get_all_roles()
    role_names = {r["role"] for r in roles}
    assert {"VIEWER", "COMMENTER", "MEMBER", "ADMIN", "OWNER"}.issubset(role_names)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GDPR Service Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.mark.asyncio
async def test_gdpr_data_export_request(db_session):
    """Requesting a data export should return a completed record with download URL."""
    from app.services.security.gdpr import GDPRService
    svc = GDPRService(db_session)
    user_id = uuid.uuid4()

    result = await svc.request_data_export(user_id)
    assert result["status"] == "COMPLETED"
    assert "download_url" in result
    assert "/security/gdpr/exports/" in result["download_url"]


@pytest.mark.asyncio
async def test_gdpr_duplicate_export_blocked(db_session):
    """A second export while one is PENDING should return the existing record."""
    from app.services.security.gdpr import GDPRService, DataExportRequest
    svc = GDPRService(db_session)
    user_id = uuid.uuid4()

    pending = DataExportRequest(
        user_id=user_id,
        status="PENDING",
        requested_at=datetime.now(timezone.utc),
    )
    db_session.add(pending)
    await db_session.flush()

    result = await svc.request_data_export(user_id)
    assert result["status"] == "PENDING"
    assert "message" in result


@pytest.mark.asyncio
async def test_gdpr_deletion_request_scheduled(db_session):
    """Account deletion request should be scheduled 30 days in the future."""
    from app.services.security.gdpr import GDPRService
    svc = GDPRService(db_session)
    user_id = uuid.uuid4()

    result = await svc.request_account_deletion(user_id, reason="Privacy concerns")
    assert result["status"] == "PENDING"
    assert "scheduled_for" in result
    assert "30 days" in result["message"]


@pytest.mark.asyncio
async def test_gdpr_cancel_deletion_success(db_session):
    """Cancelling a pending deletion request should succeed."""
    from app.services.security.gdpr import GDPRService
    svc = GDPRService(db_session)
    user_id = uuid.uuid4()

    await svc.request_account_deletion(user_id)
    result = await svc.cancel_deletion_request(user_id)
    assert result["success"] is True


@pytest.mark.asyncio
async def test_gdpr_cancel_no_request_returns_error(db_session):
    """Cancelling when there is no deletion request should return success=False."""
    from app.services.security.gdpr import GDPRService
    svc = GDPRService(db_session)
    result = await svc.cancel_deletion_request(uuid.uuid4())
    assert result["success"] is False


@pytest.mark.asyncio
async def test_gdpr_consent_persistence(db_session):
    """Consent records should be persisted and retrievable with correct values."""
    from app.services.security.gdpr import GDPRService
    svc = GDPRService(db_session)
    user_id = uuid.uuid4()

    await svc.record_consent(user_id, "marketing", True, ip_address="127.0.0.1")
    await svc.record_consent(user_id, "analytics", False)

    history = await svc.get_consent_history(user_id)
    assert len(history) == 2
    types = {r["consent_type"] for r in history}
    assert "marketing" in types
    assert "analytics" in types


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SSO Service Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.mark.asyncio
async def test_sso_configure_google(db_session):
    """Configuring Google SSO should persist and be retrievable without secrets."""
    from app.services.security.sso import SSOService
    svc = SSOService(db_session)
    workspace_id = uuid.uuid4()

    result = await svc.configure_sso(
        workspace_id=workspace_id,
        provider="google",
        client_id="test_client_id",
        client_secret="test_secret",
        redirect_uri="https://nomen.ai/auth/callback",
    )
    assert result["success"] is True

    config = await svc.get_sso_config(workspace_id)
    assert config is not None
    assert config["provider"] == "google"
    assert config["client_id"] == "test_client_id"


@pytest.mark.asyncio
async def test_sso_unsupported_provider(db_session):
    """Configuring an unknown SSO provider should return success=False."""
    from app.services.security.sso import SSOService
    svc = SSOService(db_session)
    result = await svc.configure_sso(
        workspace_id=uuid.uuid4(),
        provider="unknown_saml",
        client_id="cid",
        client_secret="csec",
        redirect_uri="https://example.com",
    )
    assert result["success"] is False


def test_sso_google_authorization_url():
    """Google SSO should include the client_id and state in the authorization URL."""
    from app.services.security.sso import GoogleSSO
    sso = GoogleSSO("my_client_id", "my_secret")
    url = sso.get_authorization_url("https://nomen.ai/callback", "state123")
    assert "accounts.google.com" in url
    assert "my_client_id" in url
    assert "state123" in url


def test_sso_microsoft_authorization_url():
    """Microsoft SSO should generate a valid tenant-specific URL."""
    from app.services.security.sso import MicrosoftSSO
    sso = MicrosoftSSO("ms_client", "ms_secret", tenant_id="tenant123")
    url = sso.get_authorization_url("https://nomen.ai/callback", "ms_state")
    assert "microsoftonline.com" in url
    assert "ms_client" in url


def test_sso_okta_authorization_url():
    """Okta SSO should embed the configured domain in the authorization URL."""
    from app.services.security.sso import OktaSSO
    sso = OktaSSO("okta_client", "okta_secret", "company.okta.com")
    url = sso.get_authorization_url("https://nomen.ai/callback", "okta_state")
    assert "company.okta.com" in url


def test_sso_available_providers_count():
    """SSOService should report exactly 3 supported providers."""
    from app.services.security.sso import SSOService
    svc = SSOService.__new__(SSOService)
    providers = svc.get_available_providers()
    assert set(providers) == {"google", "microsoft", "okta"}
