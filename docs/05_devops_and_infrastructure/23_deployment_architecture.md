# Deployment Architecture: Nomen

This document details Nomen's multi-container production environments, deployment configurations, and network isolation boundaries.

---

## 1. Container Topology

Nomen is deployment-agnostic but optimized for low-cost, high-performance container orchestration. It runs on a single VPS node (e.g. Hetzner/DigitalOcean $15/month VPS) or a cluster using Docker Compose:

```text
                  [ Public Web Traffic (HTTPS: 443) ]
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │    Traefik Reverse Proxy    │ (Let's Encrypt SSL resolver)
                   └──────┬───────────────┬──────┘
                          │               │
        ┌─────────────────┘               └─────────────────┐
        ▼ Route: /*                                         ▼ Route: /api/*
  ┌───────────────┐                                   ┌───────────────┐
  │ Next.js Web   │                                   │ FastAPI App   │
  │ (Port 3000)   │                                   │ (Port 8000)   │
  └───────────────┘                                   └───────┬───────┘
                                                              │
                                            ┌─────────────────┼─────────────────┐
                                            ▼                 ▼                 ▼
                                     ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
                                     │  PostgreSQL │   │    Redis    │   │  Cloudflare │
                                     │  Database   │   │ Broker/Cache│   │  R2 Storage │
                                     └──────▲──────┘   └──────▲──────┘   └─────────────┘
                                            │                 │
                                            └────────┐ ┌──────┘
                                                     │ │ Consume
                                                     ▼ ▼
                                            ┌─────────────────┐
                                            │ Celery Workers  │
                                            │ (Fast & Heavy)  │
                                            └─────────────────┘
```

---

## 2. Production `docker-compose.yml` Specification

Below is the deployment blueprint defining the multi-service network:

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    container_name: traefik
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@nomen.ai"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
    networks:
      - internal-net

  web:
    build:
      context: .
      dockerfile: ./docker/web/Dockerfile
    container_name: nomen_web
    environment:
      - NEXT_PUBLIC_API_URL=https://nomen.ai/api/v1
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.web.rule=Host(`nomen.ai`)"
      - "traefik.http.routers.web.entrypoints=websecure"
      - "traefik.http.routers.web.tls.certresolver=letsencrypt"
    networks:
      - internal-net

  api:
    build:
      context: .
      dockerfile: ./docker/api/Dockerfile
    container_name: nomen_api
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    environment:
      - DATABASE_URL=postgresql+asyncpg://nomen_user:${DB_PASSWORD}@postgres:5432/nomen_db
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - postgres
      - redis
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`nomen.ai`) && PathPrefix(`/api`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
    networks:
      - internal-net

  postgres:
    image: ankane/pgvector:latest  # Postgres with pgvector pre-installed
    container_name: nomen_postgres
    environment:
      - POSTGRES_USER=nomen_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=nomen_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - internal-net

  redis:
    image: redis:7-alpine
    container_name: nomen_redis
    volumes:
      - redisdata:/data
    networks:
      - internal-net

  worker_fast:
    build:
      context: .
      dockerfile: ./docker/api/Dockerfile
    container_name: nomen_worker_fast
    command: celery -A app.core.cel_app worker -Q fast-queue --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://nomen_user:${DB_PASSWORD}@postgres:5432/nomen_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - internal-net

  worker_heavy:
    build:
      context: .
      dockerfile: ./docker/api/Dockerfile
    container_name: nomen_worker_heavy
    command: celery -A app.core.cel_app worker -Q heavy-queue --loglevel=info -c 2
    environment:
      - DATABASE_URL=postgresql+asyncpg://nomen_user:${DB_PASSWORD}@postgres:5432/nomen_db
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - redis
    networks:
      - internal-net

volumes:
  pgdata:
  redisdata:

networks:
  internal-net:
    driver: bridge
```

---

## 3. Network Isolation & Security Policy
- **No Exposed Ports**: The only services exposing ports to the public internet are `traefik` (80 and 443).
- **Bridge Network**: PostgreSQL, Redis, and workers are completely unreachable from outside the host server. They communicate entirely over the internal virtual bridge network `internal-net`.
