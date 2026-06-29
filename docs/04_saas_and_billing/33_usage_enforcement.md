# Usage Enforcement

## Overview

All metered API operations enforce plan-based quotas before executing any handler logic. Quota checks run in the middleware layer, before FastAPI route handlers are invoked.

---

## Enforcement Architecture

```
HTTP Request
    │
    ▼
UsageEnforcementMiddleware
    │  ← checks path pattern
    │  ← resolves user_id from request.state
    │  ← resolves workspace_id from params/headers
    │  ← calls UsageService.check_*_quota()
    │
    ├── QUOTA OK  → forward to route handler
    └── QUOTA EXCEEDED → return HTTP 429 (short-circuit)
```

The middleware is registered in `main.py` as:
```python
app.add_middleware(UsageEnforcementMiddleware)
```

---

## Metered Operations

| Route Pattern | Action | Limit Key |
|---|---|---|
| `POST /api/v1/projects/*/generate` | AI Generation | `generations_per_month` |
| `POST /api/v1/exports/` | Export | `exports_per_month` |
| All API-key-authenticated requests | API Requests | `api_requests_per_month` |

---

## Quota Check Logic

Each check follows the same pattern:

1. **Resolve subscription**: Look up the user's active `Subscription` row
2. **Get tier**: Read the plan name / tier from the subscription
3. **Get limit**: Read `limits_json[limit_key]` from the `Plan` row
4. **Check unlimited**: If `limit == -1`, skip enforcement entirely
5. **Count usage**: Sum `UsageRecord.count` for the current billing period
6. **Enforce**: If `used >= limit`, raise `RateLimitError`

---

## HTTP 429 Response Format

When a quota is exceeded, the API returns:

```json
{
  "success": false,
  "message": "Monthly generation quota exceeded (10/10). Upgrade your plan to continue generating names.",
  "data": null,
  "errors": ["Monthly generation quota exceeded (10/10). Upgrade your plan to continue generating names."],
  "meta": {
    "request_id": "req_xxx",
    "api_version": "1.0.0"
  }
}
```

---

## Credit Balance Checks

For operations that consume credits (e.g. premium AI providers):

```python
await usage_svc.check_credit_balance(user_id, required_credits=5.0)
```

Raises `RateLimitError` when `credit_balance < required_credits`.

---

## Usage Recording

After a successful operation, record usage to enable accurate quota tracking:

```python
from app.services.billing.usage_service import UsageService, ACTION_GENERATION

usage_svc = UsageService(db)
await usage_svc.record_usage(
    user_id=current_user.id,
    workspace_id=workspace_id,
    action=ACTION_GENERATION,
    count=1,
)
```

Available action constants:
- `ACTION_GENERATION = "generation"`
- `ACTION_EXPORT = "export"`
- `ACTION_API_REQUEST = "api_request"`
- `ACTION_WORKSPACE = "workspace"`
- `ACTION_PROJECT = "project"`

---

## Monthly Resets

Usage counters reset automatically via the Celery periodic worker defined in `apps/api/app/workers/scheduler.py`.

The reset:
1. Sets `Subscription.monthly_query_count = 0`
2. Advances `Subscription.limit_reset_at` by 30 days

This happens on the first of each month (00:00 UTC) for all active subscriptions.

---

## Usage API

```
GET /api/v1/billing/usage
Authorization: Bearer <jwt>
```

Returns a complete summary of the current period's resource consumption:

```json
{
  "period_start": "2026-06-01T00:00:00Z",
  "tier": "pro",
  "actions": {
    "generation": {
      "used": 127,
      "limit": 500,
      "unlimited": false,
      "remaining": 373,
      "percent": 25.4
    },
    "export": {
      "used": 12,
      "limit": 200,
      "unlimited": false,
      "remaining": 188,
      "percent": 6.0
    },
    "api_request": {
      "used": 4521,
      "limit": 10000,
      "unlimited": false,
      "remaining": 5479,
      "percent": 45.2
    }
  }
}
```
