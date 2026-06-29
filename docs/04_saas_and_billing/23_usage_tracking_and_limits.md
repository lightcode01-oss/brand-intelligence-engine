# Usage Tracking & Limits: Nomen

This document explains how Nomen monitors user and workspace consumption counters, checks pricing tier limits, and schedules periodic usage resets.

---

## 1. Tracked Consumptions Metrics

We log usage records in the `usage_records` table whenever a billing-controlled action occurs:

- **`generation`**: Tracks generated brand names query count. Checks against monthly limits before initiating LLM provider requests.
- **`export`**: Monitors names list downloads (ReportLab PDF, CSV, JSON, MD exports).
- **`api_request`**: Measures API key requests. Free tiers are rate-limited to prevent server abuse.

---

## 2. Dynamic Limits Checks

Before executing operations (e.g. workspace creation, project generation), the application factory checks limits assigned to the user's active plan:

```python
# Limit validation pseudo-logic
if active_subscription.monthly_query_count >= active_plan.limits["monthly_generations"]:
    raise UsageLimitExceededException("Monthly generation limits reached for your current plan.")
```

---

## 3. Monthly Reset Scheduler

A Celery Beat cron task runs on the 1st of every month at midnight UTC. This job:
1. Resets `monthly_query_count` to `0` for all subscriptions.
2. Archives the previous month's usage records into cold database files for billing audits.
3. Updates workspace members with consumption warnings if active thresholds are breached.
