# Nomen: AI Brand Intelligence Platform

Nomen is an AI-powered Brand Intelligence Platform designed to discover and validate company names, domain names, and trademarks.

---

## 1. Monorepo Repository Structure

We structure this project as a **pnpm workspaces monorepo**:

```text
/
├── apps/
│   ├── web/                    <-- Next.js 15 App Router Web App
│   └── api/                    <-- FastAPI Python REST API Gateway
├── packages/
│   └── ts-config/              <-- Shared compiler parameters
├── docs/                       <-- Approved architectural specifications (30 files)
├── database/
│   └── postgres/               <-- PostgreSQL schema init files and migrations
├── docker/
│   ├── web/                    <-- Dev and Production web Dockerfiles
│   └── api/                    <-- Dev and Production API Dockerfiles
├── scripts/
│   ├── validate-env.js         <-- Environment validation script
│   └── setup.sh                <-- Local dev bootstrap script
├── .github/
│   ├── workflows/              <-- Actions workflows (CI, Lint, Security, Docker)
│   ├── ISSUE_TEMPLATE/         <-- Issue templates (Bug, Feature, Docs, Question)
│   └── pull_request_template.md
├── docker-compose.yml          <-- Production compose setup
├── docker-compose.dev.yml      <-- Local development compose setups
├── pnpm-workspace.yaml         <-- pnpm workspaces registry config
├── package.json                <-- Workspace root configs (Husky, Prettier, Lint scripts)
└── .env.example                <-- System-wide environment template
```

---

## 2. Technical Stack

- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui.
- **Backend**: FastAPI, Python 3.12, SQLAlchemy 2.0 (asyncpg), Celery Workers (with Redis).
- **Databases**: PostgreSQL (with pgvector extensions) & Redis.
- **Storage**: Cloudflare R2 (Object storage).
- **Containerization**: Docker & Docker Compose.

---

## 3. Local Workspace Setup & Installation

Follow these steps to configure your local engineering workstation:

### Prerequisites
- Install **Node.js v20.x** or higher.
- Install **pnpm v9.x**: `npm install -g pnpm`
- Install **Python 3.12** and virtualenv environments.
- Install **Docker** and Docker Compose.

### Bootstrapping
Run the automated workspace setup script to copy environment templates, initialize package dependencies, and install git hooks:
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Running Local Development Stack
Start the development database, cache, Next.js hot-reloader, and FastAPI server in Docker containers:
```bash
docker compose -f docker-compose.dev.yml up --build
```
- Web app resolves at: `http://localhost:3000`
- API endpoints resolve at: `http://localhost:8000/docs` (FastAPI Swagger view)

---

## 4. Code Quality & Formatting Rules

We enforce strict linting and formatting policies:

- **Web Code (JS, TS, HTML, CSS, JSON, YAML)**: Configured using **ESLint** and **Prettier**.
- **Python Code (FastAPI, Workers)**: Configured using **Ruff** (lint and formatting rules) and **Mypy** (strict static type validations).

### Execution Commands
```bash
pnpm run lint          # Run ESLint and Ruff linter checks
pnpm run format        # Auto-format files via Prettier and Ruff formatter
pnpm run format:check  # Dry-run format validations
```

### Git hooks (Husky)
On every `git commit`, Husky triggers **lint-staged** to format modified files automatically. Additionally, **Commitlint** checks that your commit message adheres to **Conventional Commits** guidelines.

---

## 5. Branch Strategy

We follow a structured branching model:
- **`main`**: Production deployments. Must be completely green.
- **`develop`**: Integration target for features and fixes.
- **`feature/*`**: New capabilities or architectures (e.g. `feature/scoring-updates`).
- **`fix/*`**: Bug fixes.
- **`release/*`**: Preparation logs for new versions (e.g. `release/v0.2.0`).
- **`hotfix/*`**: Emergency production patches.
