# MFA & SSO — Authentication Extensions

## TOTP Multi-Factor Authentication

### Flow

```
1. User clicks "Enable MFA"
2. POST /security/mfa/provision → returns device_id + base32 secret + OTP URI
3. Frontend renders QR code (via api.qrserver.com) and manual secret
4. User scans with Google Authenticator / Authy
5. User enters 6-digit code → POST /security/mfa/verify { device_id, code }
6. Backend verifies against ±1 TOTP windows (90s tolerance)
7. Device marked verified, 10 single-use recovery codes generated and returned
8. Recovery codes displayed once — user must store securely
```

### TOTP Implementation

- Algorithm: HMAC-SHA1 (RFC 6238 compliant)
- Digits: 6
- Period: 30 seconds
- Window tolerance: ±1 step (prev/current/next)
- Secret: 20-byte random, base32 encoded

### Recovery Codes

- 10 codes generated per activation
- 16 hex characters each (64-bit entropy)
- SHA-256 hashed before storage
- Single-use: consumed on verification, cannot be reused

## Single Sign-On (SSO)

### Supported Providers

| Provider | Protocol | Enterprise Plan |
|---|---|---|
| Google Workspace | OAuth2 + OpenID Connect | ✅ |
| Microsoft Entra ID | OAuth2 + OpenID Connect | ✅ |
| Okta | OAuth2 + OpenID Connect | ✅ |

### Configuration

```python
# Example: Configure Google SSO for a workspace
await sso_service.configure_sso(
    workspace_id=workspace_id,
    provider="google",
    client_id="...",
    client_secret="...",
    redirect_uri="https://nomen.ai/auth/sso/callback",
)
```

### Workspace Enforcement

Set `sso_required=True` in `SecurityPolicy` to enforce SSO-only login for workspace members.
Password-based login will be rejected with 403 for users in enforced workspaces.
