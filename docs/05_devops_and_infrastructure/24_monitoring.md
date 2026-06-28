# Monitoring Strategy: Nomen

This document details the telemetry tracking, metric exporters, dashboard configurations, and alerting rules of Nomen.

---

## 1. The Monitoring Stack

We leverage open-source telemetry tools combined with a cloud error-tracking service:

```text
  [ Application Metrics ]            [ Async Tasks ]            [ Code Errors ]
             │                              │                          │
             ▼                              ▼                          ▼
   ┌───────────────────┐          ┌───────────────────┐      ┌───────────────────┐
   │ Prometheus Client │          │   Celery Flower   │      │ Sentry Integrator │
   └─────────┬─────────┘          └─────────┬─────────┘      └─────────┬─────────┘
             │                              │                          │
             ▼                              ▼                          ▼
   ┌───────────────────┐             [ Admin Console ]       [ Sentry Cloud ]
   │ Grafana Dashboard │             (Worker health)         (Slack Alerts)
   └───────────────────┘
```

---

## 2. Metric Exporters & Dashboards

### 2.1. API Server Metrics (Prometheus + Grafana)
We integrate `prometheus-fastapi-instrumentator` in our API layer. It exposes an internal endpoint `/metrics` scraped by a Prometheus container every 15 seconds.
- **Request Latency (p95 / p99)**: Verifies that name search endpoints return in under 3 seconds.
- **HTTP Status Codes**: Tracks 2xx, 3xx, 4xx, and 5xx rates. A spike in 5xx codes triggers immediate support warnings.
- **Database Connection Pool Status**: Monitors active vs. idle SQLAlchemy async connections.

### 2.2. Celery Worker Telemetry (Flower)
We host a lightweight instance of **Flower** (Celery’s web monitoring dashboard) secured with basic auth behind our reverse proxy.
- **Queue Latency**: Tracks how long tasks sit in Redis before workers consume them.
- **Task Success/Failure Ratio**: Monitors the error rate of LLM APIs and Web scrapers.
- **Active Worker Pool Count**: Helps determine if we need to scale container replicas.

---

## 3. Application Telemetry (Sentry)

To capture live errors before customers report them, Sentry is integrated at the code boundaries:

### 3.1. Frontend Integration (`sentry.client.config.ts`)
Captures browser rendering exceptions, hydration failures, broken static links, and slow API interactions.

### 3.2. Backend Integration (`app/main.py`)
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration()
    ],
    traces_sample_rate=0.1,  # Trace 10% of API flows for latency profiling
)
```
Any uncaught Python exception in FastAPI routes or Celery tasks triggers a detailed trace containing environment parameters and context variables directly to Sentry.

---

## 4. Alert Threshold Rules

We configure Sentry and Prometheus to fire alerts (via webhook to our Slack channel) under these conditions:

| Incident Alert | Trigger Metric | Severity | Notification Channel |
| :--- | :--- | :--- | :--- |
| **API Server Down** | Prometheus `up == 0` for 1 minute. | Critical | PagerDuty / SMS / Slack |
| **High API Error Rates** | 5xx response rate > 2% of total traffic for 5 mins. | High | Slack / email |
| **Celery Queue Bottleneck**| Redis queue length > 50 items for 3 minutes. | Medium | Slack |
| **AI LLM Key Depleted** | Sentry catches `RateLimitError` or `AuthenticationError`. | Critical | Slack / SMS |
