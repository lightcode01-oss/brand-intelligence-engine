# Logging Architecture: Nomen

This document details Nomen's structured logging architecture, container stdout capture pipelines, log rotation rules, and central log aggregations.

---

## 1. Structured Logging Philosophy

Plain text log lines (e.g. `INFO: user logged in`) are difficult to parse, search, and aggregate. Nomen enforces **structured JSON logging** across all backend API containers and background workers using the **`structlog`** Python library.

### 1.1. Production Log Sample (JSON output)
```json
{
  "event": "name_generation_task_completed",
  "level": "info",
  "logger": "app.workers.brand_gen",
  "timestamp": "2026-06-28T20:25:00.123456Z",
  "task_id": "job_a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "execution_time_ms": 2340.5,
  "candidates_generated": 25,
  "user_id": "e4b934b1-8b94-4d89-9a7c-12f5a6f87d41"
}
```
Every log line automatically includes:
- **`timestamp`**: ISO 8601 formatting.
- **`level`**: Lowercase string (`info`, `warning`, `error`).
- **`event`**: Standardized snake_case action tag.
- **Context Metadata**: Task IDs, User IDs, execution speeds.

---

## 2. Structlog Configuration (Python Backend)

```python
# app/core/logging.py
import logging
import structlog

def setup_logging(is_production: bool = True):
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if is_production:
        # Format as compact, raw JSON string for production aggregators
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable colored output for local terminal logs
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

---

## 3. Log Levels & Volumes Policy

We apply strict rules to prevent logs from cluttering storage volumes:
- **DEBUG**: Permitted **only** in local development configurations. Banned in staging/production.
- **INFO**: Records crucial lifecycle transactions (user sign-ups, successful name generation completions, background cash flushes).
- **WARNING**: Captures retry events (e.g. LLM timeouts, slow WHOIS queries, cache misses).
- **ERROR**: Records task crashes, connection losses, and API response failures. Includes stack traces.

---

## 4. Log Rotation & Forwarding Strategy

Docker captures all writes to stdout/stderr and logs them to JSON files on the host filesystem:

- **Log Rotation Limits**: Enforced at the Docker daemon level (`/etc/docker/daemon.json`) to protect host disk storage:
  ```json
  {
    "log-driver": "json-file",
    "log-opts": {
      "max-size": "50m",
      "max-file": "3"
    }
  }
  ```
  This keeps a maximum of 150MB of logs per container, automatically rotating and deleting older records.
- **Log Aggregator (Optional, Zero-Cost)**: In staging/production, a lightweight **Vector** container reads the local Docker JSON logs and forwards them to a central, self-hosted **Grafana Loki** container, letting devs search logs instantly inside Grafana.
