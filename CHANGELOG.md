# Changelog

All notable changes to Nomen will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-06-30

### Added — Phase 5: Production Release Engineering

**Docker & Containerization**
- Enhanced multi-stage Dockerfile for API (Gunicorn+Uvicorn workers, non-root user, OCI labels)
- Enhanced multi-stage Dockerfile for Next.js (standalone output, non-root user, build-time ARGs)
- `.dockerignore` files for API and web images minimizing build context
- Full production `docker-compose.yml` with 17 services including Nginx, observability stack, Celery Beat, Certbot

**Nginx Reverse Proxy**
- Production `nginx.conf` with HTTPS-ready configuration
- HTTP/2, Gzip compression, security headers (CSP, HSTS, XSS protection)
- Rate limiting zones (API: 100/min, Auth: 10/min, Static: 500/min)
- WebSocket proxy support for real-time collaboration
- JSON structured access logging
- Static asset caching (1-year immutable for hashed Next.js assets)

**Observability Stack**
- Prometheus with full scrape configuration (API, PostgreSQL, Redis, Node exporter)
- 20+ Prometheus alert rules (API availability, latency, DB health, Redis, host resources, AI costs)
- Grafana with auto-provisioned datasources (Prometheus, Loki) and API overview dashboard
- Loki log aggregation with TSDB schema and AlertManager integration
- AlertManager with SMTP + Slack routing and severity-based escalation
- PostgreSQL exporter and Redis exporter services

**CI/CD Pipeline**
- Enhanced `ci-test.yml`: backend pytest with coverage upload, frontend type-check + build, pnpm caching
- New `cd-release.yml`: tag-based multi-arch Docker builds (amd64/arm64), GHCR push, GitHub Release creation
- Enhanced `ci-security.yml`: Bandit SAST, pip-audit CVEs, Trivy image scanning, CodeQL analysis

**Infrastructure as Code**
- Terraform `main.tf`: VPC, subnets, NAT gateway, security groups, RDS PostgreSQL 16, ElastiCache Redis, S3, Secrets Manager
- Terraform `variables.tf`: validated input variables with descriptions
- Terraform `outputs.tf`: all key resource identifiers
- Kubernetes `namespace.yaml`, enhanced `api-deployment.yaml` with security context, all three probes, Prometheus annotations
- Kubernetes `network-policy.yaml`: zero-trust pod-to-pod NetworkPolicy
- Kubernetes `hpa.yaml`: CPU/memory-based HPA for API (2-10 pods) and Web (2-8 pods)
- Updated `configmap.yaml` and `secrets.yaml` for nomen namespace

**Backup & Disaster Recovery**
- `scripts/backup-postgres.sh`: pg_dump with gzip, S3 upload, retention cleanup
- `scripts/restore-postgres.sh`: S3 download, safety confirmation, connection termination before restore

**Load Testing**
- `tests/load/k6-smoke.js`: 1 VU smoke test with strict thresholds
- `tests/load/k6-load.js`: multi-stage ramp to 50 VUs with custom metrics
- `tests/load/locustfile.py`: distributed user journey testing (public + authenticated users)

**Documentation**
- `docs/05_devops_and_infrastructure/30_deployment_guide.md`: production deployment walkthrough
- `docs/05_devops_and_infrastructure/34_security_guide.md`: security architecture and SOC2/GDPR compliance
- `docs/05_devops_and_infrastructure/35_operations_manual.md`: daily operations and incident response

**Configuration**
- Complete `.env.example` covering all 40+ production environment variables
- Updated `README.md` for v1.0.0 production release

**Bug Fixes**
- SQLite UUID type compatibility: added `@compiles(UUID, "sqlite")` returning `CHAR(32)` to prevent integer casting of UUID columns, fixing all backend tests on SQLite in-memory databases

---

## [0.1.0-foundation] — 2026-06-28

### Added
- Root monorepo workspace configuration using **pnpm workspaces**.
- Next.js 15 + React 19 boilerplate directory at `apps/web`.
- FastAPI Python API skeleton directory at `apps/api`.
- Root project tooling: Prettier, ESLint, Python Ruff, Mypy configurations.
- Pre-commit check flows managed by **Husky** and **lint-staged**.
- Continuous Integration workflows configured in `.github/workflows/`.
- Issue and Pull Request templates located in `.github/`.
- Production and local development Docker Compose settings with services health checks.
- System-wide `.env.example` configurations.

---

## Unreleased Phase Summary

The following phases were implemented between foundation and v1.0.0:

| Phase | Description |
|---|---|
| Phase 1 | Core brand intelligence engine: AI name generation, brand scoring, domain/trademark checking |
| Phase 2 | SaaS foundations: authentication, JWT, workspace management, PostgreSQL models |
| Phase 3 | Marketing website (65 pages), billing integration, Celery workers |
| Phase 3.4 | Full marketing site: landing, pricing, blog, docs, careers, legal pages, SEO |
| Phase 4.0 | Real-time collaboration: comments, mentions, notifications, favorites, collections, activity feeds |
| Phase 4.1 | Enterprise analytics: 7 dashboard pages, insights engine, recommendations, reports, admin portal |
| Phase 4.2 | Enterprise security: SSO, MFA (TOTP), session management, RBAC, GDPR tooling, audit logs |
| Phase 4.3 | AI optimization: circuit breaker, failover routing, semantic caching, integrations (Slack/Discord/Teams/Zapier/webhooks), Prometheus metrics, 9 admin portals |
| Phase 5 | Production release engineering: Docker, Nginx, CI/CD, Terraform, K8s, observability, security hardening, load testing, documentation |
