# Changelog

All notable changes to Nomen will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-foundation] - 2026-06-28

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
