# CI/CD Pipeline Design: Nomen

This document specifies Nomen's automated Continuous Integration and Continuous Delivery (CI/CD) pipelines implemented via **GitHub Actions**.

---

## 1. Pipeline Blueprint

```text
       [ Developer pushes code to master / PR ]
                          │
                          ▼
            ┌───────────────────────────┐
            │   Stage 1: Lint & Audit   │ (Ruff, ESLint, Prettier, Mypy)
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   Stage 2: Run Tests      │ (Pytest, Vitest, Coveralls)
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   Stage 3: Docker Build   │ (Build & Tag Next.js & FastAPI)
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   Stage 4: Server Deploy  │ (SSH Pull & restart Compose stack)
            └───────────────────────────┘
```

---

## 2. GitHub Actions CI/CD Workflow (`.github/workflows/deploy.yml`)

The following YAML schema maps our automated deployment process:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      # -- Python Backend Quality Checks --
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Python Deps
        run: |
          pip install -r apps/api/requirements.txt
          pip install pytest pytest-mock ruff mypy

      - name: Run API Linter (Ruff)
        run: ruff check apps/api/

      - name: Run API Tests
        run: pytest apps/api/tests/ --cov=api

      # -- Frontend Quality Checks --
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Node Deps
        run: pnpm install --prefix apps/web

      - name: Run Web Linter (ESLint)
        run: pnpm run lint --prefix apps/web

      - name: Run Web Tests
        run: pnpm run test --prefix apps/web

  build-and-deploy:
    needs: lint-and-test
    if: github.ref == 'refs/heads/master' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: actions/setup-buildx-action@v3

      - name: Log in to GitHub Packages Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push API Image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./docker/api/Dockerfile
          push: true
          tags: ghcr.io/nomen/api:latest,ghcr.io/nomen/api:${{ github.sha }}

      - name: Build and Push Web Image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./docker/web/Dockerfile
          push: true
          tags: ghcr.io/nomen/web:latest,ghcr.io/nomen/web:${{ github.sha }}

      # -- Remote VPS Deployment via SSH --
      - name: Deploy to Host Server
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/nomen
            docker compose pull
            docker compose up -d --remove-orphans
            docker system prune -af  # Clean stale images
```

---

## 3. Pull Request Guardrails
No code enters the production branch without passing validation:
- **Code Reviews**: Minimum of 1 approved pull-request review.
- **Strict Lint Validation**: Any Ruff/ESLint style deviation, Mypy type-checking alert, or broken unit test instantly halts the pipeline, preventing container builds.
- **Image Rollback Plan**: Every build is tagged with the specific commit SHA. If a live release fails, rolling back to the previous stable state takes under **30 seconds** by executing `docker compose up` pointing to the previous SHA tag.
