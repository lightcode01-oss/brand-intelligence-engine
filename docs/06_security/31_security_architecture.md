# Security Architecture — Nomen Brand Intelligence Platform

## Overview

Phase 4.2 introduces a multi-layer enterprise security architecture with zero-trust principles,
immutable audit logging, and GDPR-compliant data governance.

## Security Layers

```
┌──────────────────────────────────────────────────────────────────┐
│                        REQUEST LIFECYCLE                         │
├──────────────┬──────────────┬─────────────┬─────────────────────┤
│  Transport   │   Auth/JWT   │    RBAC     │   Audit & Events    │
│  (HTTPS/TLS) │  + MFA Gate  │  Permission │   (Immutable Log)   │
└──────────────┴──────────────┴─────────────┴─────────────────────┘
```

## Models

| Model | Purpose |
|---|---|
| `UserSession` | Device-tracked sessions with revocation |
| `MFADevice` | TOTP authenticator device registrations |
| `RecoveryCode` | Single-use MFA backup codes |
| `SecurityEvent` | Immutable audit trail records |
| `SecurityPolicy` | Workspace-level security configuration |
| `SSOProvider` | OAuth2/OIDC provider configurations |
| `DataExportRequest` | GDPR Art. 20 export request queue |
| `DataDeletionRequest` | GDPR Art. 17 erasure request queue |
| `ConsentRecord` | User consent audit trail |

## Services

| Service | Location |
|---|---|
| `MFAService` | `services/security/mfa.py` |
| `SessionManager` | `services/security/sessions.py` |
| `AuditService` | `services/security/audit.py` |
| `RBACService` | `services/security/rbac.py` |
| `GDPRService` | `services/security/gdpr.py` |
| `SSOService` | `services/security/sso.py` |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/security/mfa/status` | MFA enrollment status |
| POST | `/security/mfa/provision` | Provision TOTP device |
| POST | `/security/mfa/verify` | Verify and activate MFA |
| DELETE | `/security/mfa/disable` | Disable MFA |
| GET | `/security/sessions` | List active sessions |
| DELETE | `/security/sessions/{id}` | Revoke session |
| DELETE | `/security/sessions` | Revoke all sessions |
| GET | `/security/audit` | Personal audit log |
| GET | `/security/audit/workspace` | Workspace audit trail |
| GET | `/security/audit/compliance` | SOC 2 compliance report |
| POST | `/security/gdpr/export` | Request data export |
| POST | `/security/gdpr/delete` | Request account deletion |
| DELETE | `/security/gdpr/delete/cancel` | Cancel deletion |
| POST | `/security/gdpr/consent` | Record consent |
| GET | `/security/sso/config` | Get SSO config |
| POST | `/security/sso/configure` | Configure SSO provider |
| POST | `/security/rbac/assign` | Assign workspace role |
| GET | `/security/rbac/members` | List members with roles |

## Frontend Pages

| Route | Component |
|---|---|
| `/security` | Security Center overview with score |
| `/security/mfa` | TOTP setup wizard + recovery codes |
| `/security/sessions` | Session manager with per-device revocation |
| `/security/audit` | Audit log viewer with risk visualization |
| `/security/sso` | SSO provider configuration form |
| `/security/privacy` | GDPR consent + export + deletion controls |
