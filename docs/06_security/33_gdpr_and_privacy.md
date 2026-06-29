# GDPR & Privacy Compliance

## Data Subject Rights (GDPR Articles)

| Right | Article | Implementation |
|---|---|---|
| Right to Access | Art. 15 | Audit log viewer at `/security/audit` |
| Right to Portability | Art. 20 | `POST /security/gdpr/export` → archive download |
| Right to Erasure | Art. 17 | `POST /security/gdpr/delete` → 30-day grace period |
| Right to Object | Art. 21 | Consent management at `/security/privacy` |
| Right to Rectification | Art. 16 | Profile settings update |

## Data Export

- Triggered by `POST /security/gdpr/export`
- Status lifecycle: `PENDING → PROCESSING → COMPLETED`
- Download link expires after 7 days
- One pending export per user enforced
- Archive covers: profile, workspaces, projects, generations, billing, audit events

## Account Deletion

- 30-day grace period from request to execution
- User can cancel before scheduled_for date
- On completion: all PII anonymized, records pseudonymized
- Billing data retained per tax compliance requirements (7 years)

## Consent Tracking

```python
# Record a consent event
await gdpr_service.record_consent(
    user_id=user.id,
    consent_type="marketing",  # marketing | analytics | necessary
    granted=True,
    ip_address="...",
)
```

Consent records are **immutable** — each change creates a new record for full audit trail.

## Data Retention Policies

| Data Category | Retention Period |
|---|---|
| Security events | 1 year |
| Consent records | Permanent (immutable) |
| Audit logs | 2 years |
| Billing invoices | 7 years (tax law) |
| Export archives | 7 days after generation |
| Session records | 90 days after expiry |
