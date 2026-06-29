# Operations Manual — Nomen v1.0.0

## System Overview

Nomen runs as a containerized multi-service application managed by Docker Compose in production. Core services:

| Service | Container | Port (internal) |
|---|---|---|
| Nginx reverse proxy | `nomen_nginx` | 80, 443 |
| Next.js frontend | `nomen_web` | 3000 |
| FastAPI backend | `nomen_api` | 8000 |
| PostgreSQL | `nomen_postgres` | 5432 |
| Redis | `nomen_redis` | 6379 |
| Celery fast worker | `nomen_worker_fast` | — |
| Celery heavy worker | `nomen_worker_heavy` | — |
| Celery beat | `nomen_celery_beat` | — |
| Celery Flower | `nomen_flower` | 5555 |
| Prometheus | `nomen_prometheus` | 9090 |
| Grafana | `nomen_grafana` | 3001 |
| Loki | `nomen_loki` | 3100 |
| AlertManager | `nomen_alertmanager` | 9093 |

---

## Daily Operations

### Health Check Dashboard

Access Grafana at `http://your-server:3001` with admin credentials.

Quick CLI health check:
```bash
# All services
docker compose ps

# API health
curl -s https://nomen.ai/health | python3 -m json.tool

# Database connections
docker compose exec postgres psql -U nomen_user -d nomen_db \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Redis memory
docker compose exec redis redis-cli info memory | grep used_memory_human
```

### Log Access

```bash
# Live API logs
docker compose logs -f api

# Structured search (requires jq)
docker compose logs api | grep '"level":"ERROR"' | jq .

# Nginx access log — last 100 requests
docker compose logs nginx | tail -100

# All services last 5 minutes
docker compose logs --since 5m
```

---

## Incident Response

### API Down

**Symptoms**: 502 Bad Gateway from Nginx, health check failing

```bash
# 1. Check API container status
docker compose ps api

# 2. View recent logs
docker compose logs --tail=100 api

# 3. Restart API
docker compose restart api

# 4. If still failing, rebuild
docker compose up -d --no-deps --build api
```

### Database Connection Exhausted

**Symptoms**: `asyncpg.TooManyConnectionsError` in API logs

```bash
# Check connection count
docker compose exec postgres psql -U nomen_user -d nomen_db \
  -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Terminate idle connections > 5 minutes
docker compose exec postgres psql -U nomen_user -d nomen_db \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity \
      WHERE state = 'idle' AND query_start < NOW() - INTERVAL '5 minutes';"
```

### Redis Memory Full

**Symptoms**: Redis returning `OOM` errors, cache misses spike

```bash
# Check memory
docker compose exec redis redis-cli info memory

# Flush expired keys
docker compose exec redis redis-cli DEBUG SLEEP 0

# Emergency flush (WARNING: clears all cache)
# docker compose exec redis redis-cli FLUSHDB
```

### High CPU

```bash
# Identify which container
docker stats --no-stream

# Check Celery queue depth
docker compose exec redis redis-cli LLEN celery

# Temporarily scale up workers
docker compose up -d --scale worker_fast=4
```

---

## Maintenance Procedures

### Planned Maintenance Window

1. Enable maintenance mode:
   ```bash
   docker compose exec api python -c "
   from app.core.config import settings
   # Update MAINTENANCE_MODE=true in .env then restart
   "
   # OR set MAINTENANCE_MODE=true in .env and restart API
   ```

2. Perform maintenance

3. Disable maintenance mode and verify

### Database Schema Migration

```bash
# Always backup before migration
./scripts/backup-postgres.sh production

# Run migration
docker compose run --rm api alembic upgrade head

# Verify
docker compose run --rm api alembic current
```

### Dependency Updates

```bash
# Backend
cd apps/api
pip list --outdated
# Update requirements.txt
# Run tests: python -m pytest -o asyncio_mode=auto -v

# Frontend
cd apps/web
npm outdated
# Update package.json
# Run: npm install && npm run lint && npm run build
```

---

## Backup Procedures

See [Backup Guide](./36_backup_guide.md).

Quick backup:
```bash
./scripts/backup-postgres.sh production
```

---

## Scaling

### Horizontal Scaling (Docker Compose)

```bash
# Scale API to 4 instances (Nginx load balances automatically)
docker compose up -d --scale api=4
docker compose up -d --scale worker_fast=4
```

### Vertical Scaling

Update resource limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: "4.0"      # Increase from 2.0
      memory: 2G       # Increase from 1G
```

---

## Monitoring Thresholds

| Metric | Warning | Critical | Action |
|---|---|---|---|
| API error rate | >2% | >5% | Check logs, restart |
| API p99 latency | >3s | >8s | Scale up workers |
| CPU usage | >70% | >90% | Scale horizontally |
| Memory usage | >80% | >95% | Scale vertically |
| Disk usage | >70% | >85% | Archive/clean logs |
| DB connections | >80% max | >95% max | Tune pool size |
| Redis memory | >80% | >90% | Increase maxmemory |
| Celery queue depth | >100 | >500 | Scale workers |

---

## Contact & Escalation

| Level | Contact | SLA |
|---|---|---|
| P0 Critical (Production down) | oncall@nomen.ai + PagerDuty | 15 min response |
| P1 High (Degraded performance) | platform@nomen.ai | 1 hour response |
| P2 Medium (Non-critical issue) | support@nomen.ai | 4 hour response |
| P3 Low (Enhancement/question) | GitHub Issues | 1 business day |
