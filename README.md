# Nomen: AI Brand Intelligence Platform

> **v1.0.0 Production Release** — The complete AI-powered platform for discovering, validating, and managing company names, domains, and trademarks.

---

## Platform Overview

Nomen is an enterprise-grade Brand Intelligence Platform built for founders, brand strategists, and marketing teams. It provides:

- **AI Name Generation** — Multi-provider AI (Gemini, OpenAI, Anthropic) with failover routing
- **Brand Score Intelligence** — Pronounceability, domain, trademark, and semantic scoring
- **Domain Availability** — Real-time domain and social handle checking
- **Trademark Analysis** — AI-powered trademark risk assessment
- **Real-time Collaboration** — Comments, mentions, activity feeds, and live generation progress
- **Enterprise Security** — SSO, MFA (TOTP), RBAC, audit logs, GDPR tooling
- **Analytics Dashboard** — Credits, usage, team activity, workspace growth, AI performance
- **SaaS Billing** — Stripe integration with multiple plan tiers and usage tracking
- **Developer API** — REST API with API keys, webhooks, and comprehensive OpenAPI docs

---

## Repository Structure

```text
/
├── apps/
│   ├── web/                          Next.js 15 App Router — 65 routes
│   └── api/                          FastAPI Python backend — 50+ endpoints
├── packages/
│   └── ts-config/                    Shared TypeScript compiler config
├── docs/                             30+ architectural documentation files
├── docker/
│   ├── api/                          Multi-stage API Dockerfile
│   ├── web/                          Multi-stage Next.js Dockerfile
│   ├── nginx/                        Production Nginx reverse proxy config
│   └── monitoring/                   Prometheus, Grafana, Loki, AlertManager
├── kubernetes/                       Production K8s manifests (10 files)
├── terraform/                        AWS infrastructure as code
├── scripts/                          Backup, restore, and operational scripts
├── tests/
│   └── load/                         k6 and Locust load testing scripts
├── .github/
│   └── workflows/                    CI/CD pipelines (test, lint, security, release)
├── docker-compose.yml                Full production stack (17 services)
├── docker-compose.dev.yml            Local development stack
└── .env.example                      Complete environment template
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15, React 19, TypeScript 5, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy 2.0 async, Pydantic v2 |
| **Database** | PostgreSQL 16 + pgvector extension |
| **Cache / Queue** | Redis 7 + Celery 5 |
| **AI Providers** | Google Gemini, OpenAI GPT-4, Anthropic Claude (with failover) |
| **Payments** | Stripe |
| **Reverse Proxy** | Nginx (HTTPS, HTTP/2, gzip, rate limiting, security headers) |
| **Observability** | Prometheus, Grafana, Loki, AlertManager |
| **CI/CD** | GitHub Actions (test, lint, security scan, multi-arch Docker build) |
| **Infrastructure** | Docker Compose (production), Kubernetes, Terraform (AWS) |

---

## Quick Start

### Prerequisites

- Node.js 20+, pnpm 9+
- Python 3.12+
- Docker + Docker Compose

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/your-org/nomen.git && cd nomen

# 2. Copy environment template
cp .env.example .env
# Edit .env with your API keys

# 3. Start development stack
docker compose -f docker-compose.dev.yml up --build

# Web app:  http://localhost:3000
# API docs: http://localhost:8000/docs
# Flower:   http://localhost:5555
```

### Running Tests

```bash
# Backend tests (107 tests)
cd apps/api
python -m pytest -o asyncio_mode=auto -v

# Frontend lint
npm --prefix apps/web run lint

# Frontend build verification
npm --prefix apps/web run build
```

---

## Production Deployment

See the [Deployment Guide](docs/05_devops_and_infrastructure/30_deployment_guide.md) for complete instructions.

**Quick start:**
```bash
cp .env.example .env && nano .env          # Fill in production values
docker compose pull && docker compose up -d
curl https://nomen.ai/health               # Verify
```

---

## Documentation

| Document | Description |
|---|---|
| [Deployment Guide](docs/05_devops_and_infrastructure/30_deployment_guide.md) | Production deployment walkthrough |
| [Security Guide](docs/05_devops_and_infrastructure/34_security_guide.md) | Security architecture and compliance |
| [Operations Manual](docs/05_devops_and_infrastructure/35_operations_manual.md) | Day-to-day operations and incident response |
| [Monitoring Guide](docs/05_devops_and_infrastructure/24_monitoring.md) | Prometheus, Grafana, and alert configuration |
| [Disaster Recovery](docs/05_devops_and_infrastructure/29_disaster_recovery_runbook.md) | Backup and recovery procedures |
| [System Architecture](docs/02_system_architecture/) | Full platform architecture specs |
| [API Docs](https://nomen.ai/api/docs) | Interactive FastAPI Swagger UI |

---

## CI/CD Status

| Pipeline | Status |
|---|---|
| Tests | ![Tests](https://github.com/your-org/nomen/actions/workflows/ci-test.yml/badge.svg) |
| Security | ![Security](https://github.com/your-org/nomen/actions/workflows/ci-security.yml/badge.svg) |
| Release | ![Release](https://github.com/your-org/nomen/actions/workflows/cd-release.yml/badge.svg) |

---

## Code Quality

```bash
pnpm lint              # ESLint (frontend) + Ruff (backend)
pnpm format            # Prettier + Ruff formatter
```

**Enforcement**: Pre-commit hooks (Husky + lint-staged) run on every `git commit`.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
