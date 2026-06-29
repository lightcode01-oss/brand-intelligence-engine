# Deployment Guide — Nomen v1.0.0

## Overview

This guide covers deploying Nomen to a production Linux server using Docker Compose with Nginx as the reverse proxy. For Kubernetes deployments, see the [Kubernetes Guide](./32_cicd_guide.md).

---

## Prerequisites

| Requirement | Version |
|---|---|
| Linux (Ubuntu 22.04 LTS recommended) | 22.04+ |
| Docker | 25.0+ |
| Docker Compose | 2.24+ |
| Domain name | DNS A record pointing to server IP |
| Minimum server spec | 4 vCPU, 8GB RAM, 100GB SSD |

---

## 1. Server Preparation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

---

## 2. Clone & Configure

```bash
# Clone repository
git clone https://github.com/your-org/nomen.git /opt/nomen
cd /opt/nomen

# Copy environment template
cp .env.example .env

# Edit .env with production values (REQUIRED)
nano .env
```

### Required `.env` Values

| Variable | Description |
|---|---|
| `DB_PASSWORD` | Strong 32+ char random password |
| `SECRET_KEY` | `openssl rand -hex 32` |
| `GEMINI_API_KEY` | From Google AI Studio |
| `STRIPE_SECRET_KEY` | From Stripe dashboard |
| `STRIPE_WEBHOOK_SECRET` | From Stripe webhook config |
| `NEXTAUTH_SECRET` | `openssl rand -base64 32` |
| `SMTP_*` | Email provider credentials |

---

## 3. SSL Certificate Setup

### Option A: Let's Encrypt (recommended)

```bash
# Create ssl directory
mkdir -p docker/nginx/ssl

# Start nginx briefly for ACME challenge
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email admin@nomen.ai \
  --agree-tos \
  --no-eff-email \
  -d nomen.ai \
  -d www.nomen.ai

# Generate DH params (run once — takes ~2 min)
openssl dhparam -out docker/nginx/ssl/dhparam.pem 2048

# Copy Let's Encrypt certs
cp /etc/letsencrypt/live/nomen.ai/fullchain.pem docker/nginx/ssl/
cp /etc/letsencrypt/live/nomen.ai/privkey.pem docker/nginx/ssl/
```

### Option B: Self-signed (staging only)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/privkey.pem \
  -out docker/nginx/ssl/fullchain.pem \
  -subj "/CN=nomen.ai"
openssl dhparam -out docker/nginx/ssl/dhparam.pem 2048
```

---

## 4. Database Initialization

```bash
# Start only PostgreSQL first
docker compose up -d postgres

# Wait for health check
docker compose ps postgres

# Run Alembic migrations
docker compose run --rm api \
  alembic -c alembic.ini upgrade head
```

---

## 5. Production Launch

```bash
# Pull/build all images
docker compose pull
docker compose build --no-cache

# Start all services
docker compose up -d

# Verify all services are healthy
docker compose ps
docker compose logs --tail=50 api
docker compose logs --tail=50 web
```

---

## 6. Health Verification

```bash
# Check all container statuses
docker compose ps

# Test API health endpoint
curl https://nomen.ai/api/v1/health

# Test web frontend
curl -I https://nomen.ai

# Check Prometheus metrics
curl http://localhost:9090/-/healthy

# Check Grafana
curl http://localhost:3001/api/health
```

---

## 7. Maintenance

### Zero-downtime API restart

```bash
docker compose up -d --no-deps --build api
```

### Database backup

```bash
./scripts/backup-postgres.sh production
```

### Log viewing

```bash
docker compose logs -f api         # API logs
docker compose logs -f nginx        # Access logs
docker compose logs -f worker_fast  # Celery fast queue logs
```

### Scale API horizontally

```bash
docker compose up -d --scale api=4
```

---

## 8. SSL Certificate Renewal

Certbot auto-renews every 12 hours (configured in docker-compose.yml). To manually renew:

```bash
docker compose exec certbot certbot renew --quiet
docker compose exec nginx nginx -s reload
```

---

## 9. Rollback Procedure

```bash
# Stop current containers
docker compose down

# Pull previous version
export TAG=v0.9.0
docker compose pull

# Restore previous database backup if needed
./scripts/restore-postgres.sh /var/backups/nomen/nomen_production_YYYYMMDD.sql.gz

# Start previous version
docker compose up -d
```

---

## Related Guides

- [Docker Guide](./31_docker_guide.md)
- [CI/CD Guide](./32_cicd_guide.md)
- [Monitoring Guide](./33_monitoring_guide.md)
- [Backup Guide](./36_backup_guide.md)
- [Disaster Recovery](../05_devops_and_infrastructure/29_disaster_recovery_runbook.md)
