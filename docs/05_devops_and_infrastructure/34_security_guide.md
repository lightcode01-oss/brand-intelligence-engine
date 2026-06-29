# Security Guide — Nomen v1.0.0

## Security Architecture

Nomen implements a defense-in-depth security model with controls at every layer.

---

## 1. Transport Security

### HTTPS / TLS
- TLS 1.2 minimum, TLS 1.3 preferred
- Strong cipher suite (ECDHE, AES-GCM, CHACHA20)
- HSTS header: `max-age=31536000; includeSubDomains; preload`
- Certificate managed by Let's Encrypt (auto-renewed)
- Forward Secrecy via DHE/ECDHE key exchange

### HTTP Security Headers (Nginx + FastAPI middleware)

| Header | Value |
|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` |
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Content-Security-Policy` | See Nginx config |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` |

---

## 2. Authentication & Authorization

### JWT Tokens
- Algorithm: HS256 (upgrade to RS256 for enterprise SSO)
- Access token TTL: 15 minutes
- Refresh token TTL: 7 days
- Tokens invalidated on password change / logout
- `SECRET_KEY`: minimum 256-bit entropy

### MFA (Phase 4.2)
- TOTP (RFC 6238 compliant, Google Authenticator compatible)
- Recovery codes (8 × 16-char codes, bcrypt-hashed in DB)
- WebAuthn/FIDO2 ready architecture

### RBAC
- Workspace-scoped roles: `owner`, `admin`, `member`, `viewer`
- Permission checks at service layer (not just route level)
- Principle of least privilege throughout

---

## 3. API Security

### Rate Limiting
- Global: 60 req/min per IP (configurable via `RATE_LIMIT_PER_MINUTE`)
- Auth endpoints: 10 req/min per IP (Nginx zone: `auth_limit`)
- Implemented via Redis sliding window

### CORS
- Allowed origins explicitly set via `CORS_ORIGINS` env var
- Credentials allowed only for allowlisted origins
- Methods and headers restricted

### Input Validation
- Pydantic v2 models validate all request bodies
- Path/query parameters validated by FastAPI
- File uploads: type checking, size limits (10MB max via Nginx)

### Request Signing
- Outbound webhooks signed with HMAC-SHA256
- Header: `X-Nomen-Signature: sha256=<signature>`

---

## 4. Data Security

### Database
- PostgreSQL with encrypted connections (`sslmode=require` in production)
- Passwords hashed with bcrypt (cost factor: 12)
- Sensitive fields encrypted at rest (RDS storage encryption)
- Soft deletes with `deleted_at` timestamps (no hard deletes)

### Secrets Management
- All secrets via environment variables — never hardcoded
- Production: AWS Secrets Manager or HashiCorp Vault
- `.env` files excluded from git (`.gitignore`)
- Kubernetes: use Sealed Secrets or External Secrets Operator

### Backup Encryption
- Database backups encrypted at rest (AES-256 via S3 SSE)
- Backup retention: 30 days local, 90 days S3
- Backup access restricted to IAM role with minimal permissions

---

## 5. Container Security

### Docker
- Non-root users in all containers (`appuser`, UID 10001)
- Read-only root filesystems where possible
- No `privileged` mode containers
- Docker socket not mounted in application containers

### Kubernetes
- `securityContext.runAsNonRoot: true`
- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true`
- Capabilities dropped: `ALL`
- NetworkPolicy: zero-trust pod-to-pod communication
- Pod Security Admission: Restricted profile

### Image Security
- Multi-stage builds (build tools not in runtime image)
- Trivy vulnerability scanning in CI pipeline
- Images pinned to specific versions/digests
- GHCR private registry with pull authentication

---

## 6. Operational Security

### Audit Logging
- All authentication events logged (login, logout, MFA, password change)
- Admin actions logged with actor, timestamp, and IP
- GDPR data requests logged
- Logs shipped to Loki, retained 90 days

### Incident Response

1. **Detected**: Monitor Prometheus alerts and Grafana dashboards
2. **Triage**: Check API error rates, authentication anomalies
3. **Contain**: Revoke compromised tokens via admin API
4. **Investigate**: Review structured logs in Loki
5. **Remediate**: Patch, rotate secrets, redeploy
6. **Report**: Document in incident report

### Secret Rotation Checklist

```bash
# Rotate JWT secret (invalidates all sessions)
openssl rand -hex 32
# Update SECRET_KEY in production secrets
# Redeploy API service

# Rotate database password
# Update DB_PASSWORD in production secrets
# Update RDS password
# Redeploy all services

# Rotate API keys (Gemini, OpenAI, Stripe)
# Regenerate in respective dashboards
# Update in secrets manager
# Redeploy services
```

---

## 7. Compliance Checklist

### SOC 2 Type II Readiness

| Control | Status |
|---|---|
| Access Control (CC6) | ✅ RBAC + MFA + Session management |
| Logical & Physical Access Controls (CC6.1) | ✅ JWT + bcrypt + HTTPS |
| System Operations Monitoring (CC7) | ✅ Prometheus + Grafana + AlertManager |
| Change Management (CC8) | ✅ CI/CD with approval gates |
| Risk Mitigation (CC9) | ✅ Security scanning in CI |
| Availability (A1) | ✅ HPA + health checks + multi-AZ |
| Confidentiality (C1) | ✅ Encryption at rest + in transit |

### GDPR Compliance

- Data export: `GET /api/v1/gdpr/export` (Phase 4.2)
- Data deletion: `POST /api/v1/gdpr/delete` (Phase 4.2)
- Consent tracking in user model
- DPA (Data Processing Agreement) template in `docs/legal/`

---

## Related

- [Operations Manual](./35_operations_manual.md)
- [Disaster Recovery](./29_disaster_recovery_runbook.md)
