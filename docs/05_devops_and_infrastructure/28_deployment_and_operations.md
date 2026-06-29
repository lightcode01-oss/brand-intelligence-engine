# Deployment & Operations Guide: Nomen

This guide details steps for deploying the Nomen Brand Intelligence platform to production systems using Docker Compose or Kubernetes orchestrators.

---

## 1. Production Configuration Checklist

Before deployment, verify the following configuration keys inside `secrets.yaml` or `.env` files:

- **`SECRET_KEY`**: Set a high-entropy string to sign JWT tokens.
- **`DATABASE_URL`**: production PostgreSQL connection string (use pgpool or connection pooling).
- **`REDIS_URL`**: High-availability Redis URL (Redis Sentinel or Cluster).
- **`GEMINI_API_KEY`** & **`OPENAI_API_KEY`**: Active tokens to query LLM models.

---

## 2. Docker Compose Production Run

To stand up the complete platform stack (Web, API, Postgres, Redis, Celery, Traefik gateway, Prometheus/Grafana monitoring, Loki logs collector) in production:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 3. Kubernetes Deployment

To deploy to a cloud Kubernetes cluster (e.g. EKS, GKE, AKS, or bare-metal):

### 3.1. Apply Global Properties
```bash
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml
```

### 3.2. Deploy Services
```bash
kubectl apply -f kubernetes/postgres-statefulset.yaml
kubectl apply -f kubernetes/redis-deployment.yaml
kubectl apply -f kubernetes/celery-deployment.yaml
kubectl apply -f kubernetes/api-deployment.yaml
kubectl apply -f kubernetes/web-deployment.yaml
```

### 3.3. Configure Routing & Autoscaling
```bash
kubectl apply -f kubernetes/ingress.yaml
kubectl apply -f kubernetes/hpa.yaml
```

---

## 4. Monitoring & Metrics Scraping

- **Endpoint**: Prometheus gathers statistics from the API service `/api/v1/metrics` route.
- **Telemetry**: Gauge details are scraped every 15 seconds. Ensure the Ingress controller exposes the `/metrics` endpoint to the Prometheus cluster only.
