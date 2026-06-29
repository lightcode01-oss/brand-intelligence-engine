# Audit & Compliance — SOC 2 Readiness

## Security Event Tracking

All security-relevant events are recorded as immutable `SecurityEvent` records.

### Tracked Events

| Event Type | Risk Score | Trigger |
|---|---|---|
| `LOGIN_SUCCESS` | 0 | Successful authentication |
| `LOGIN_FAILED` | 20 | Failed password or MFA attempt |
| `MFA_ENABLED` | 10 | MFA device activated |
| `MFA_DISABLED` | 50 | MFA removed from account |
| `SESSION_REVOKED` | 10 | Session terminated |
| `PASSWORD_CHANGED` | 30 | Password update |
| `ROLE_CHANGED` | 40 | Workspace role assignment |
| `EXPORT_REQUESTED` | 5 | Generation export created |
| `API_KEY_CREATED` | 15 | New API key issued |
| `ACCOUNT_LOCKED` | 70 | Brute-force lockout triggered |
| `DATA_DELETION_REQUESTED` | 80 | GDPR erasure request |

### Anomaly Detection

`AuditService.get_failed_login_count(actor, since_minutes)` enables brute-force detection.
Integrate with account lockout policy: lock after 5 failures in 15 minutes.

## Compliance Reports

```python
# Generate SOC 2 compliance report
report = await audit_service.get_compliance_report(
    workspace_id=workspace_id,
    since_days=30,
)
# Returns: period, high_risk_summary, all events
```

## SOC 2 Trust Services Criteria Mapping

| Criteria | Implementation |
|---|---|
| CC6.1 — Logical access | JWT + RBAC + MFA |
| CC6.2 — Authentication | TOTP, SSO, session tokens |
| CC6.3 — Revocation | Session revocation API |
| CC7.2 — Anomalies | Risk scoring, failed-login tracking |
| CC7.3 — Evaluation | Compliance report endpoint |
| A1.2 — Availability | Health check endpoints |
| PI1.1 — Data integrity | Immutable audit records |
| P1.1 — Privacy notice | Consent management |
| P4.2 — Data retention | Configurable retention policies |
| P8.1 — Data requests | GDPR export + deletion endpoints |
