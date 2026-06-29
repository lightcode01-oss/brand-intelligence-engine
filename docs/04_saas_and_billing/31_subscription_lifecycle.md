# Subscription Lifecycle

## States

```
                    ┌──────────────────────────────────────────┐
                    │              SUBSCRIPTION FSM              │
                    └──────────────────────────────────────────┘

  [New User]
      │
      ▼
  FREE (auto-created)
      │
      │  checkout.completed webhook / upgrade API
      ▼
  ACTIVE ◄──────────────────────────────────────────┐
      │                                              │
      │  invoice.payment_failed                      │  resume API
      ▼                                              │
  PAST_DUE ──── invoice.paid ──────────────────── ACTIVE
      │
      │  manual cancel or non-payment
      ▼
  CANCELED ──── resume API (if within period) ─► ACTIVE
      │
      │  period ends
      ▼
  FREE (auto-downgraded on subscription.cancelled webhook)
```

---

## Plan Tiers

| Plan | Price | Generations/mo | Exports/mo | API Requests/mo | Team Members |
|---|---|---|---|---|---|
| **Free** | $0 | 10 | 5 | 100 | 1 |
| **Starter** | $9 | 100 | 50 | 1,000 | 3 |
| **Pro** | $29 | 500 | 200 | 10,000 | 10 |
| **Business** | $99 | 2,000 | 1,000 | 50,000 | 50 |
| **Enterprise** | Custom | Unlimited | Unlimited | Unlimited | Unlimited |

---

## Key Operations

### Checkout (new subscription)

```
POST /api/v1/billing/checkout
{
  "plan_name": "pro",
  "success_url": "https://app.nomen.ai/billing?success=1",
  "cancel_url": "https://app.nomen.ai/billing",
  "trial_days": 14,
  "coupon_code": "SAVE20"
}
```

Response contains `checkout_url` — redirect the user there.

### Upgrade

```
POST /api/v1/billing/checkout
{ "plan_name": "business", ... }
```

Upgrades apply proration immediately (charged the difference).

### Cancel

```
POST /api/v1/billing/cancel
```

Subscription moves to `CANCELED` state. User retains access until `limit_reset_at`.

### Resume

```
POST /api/v1/billing/resume
```

Only valid while `status = CANCELED` and the billing period hasn't ended.

### Customer portal

```
POST /api/v1/billing/portal
{ "return_url": "https://app.nomen.ai/billing" }
```

Returns `portal_url` — redirect the user to manage payment methods, download past invoices.

---

## Credit Grants on Plan Activation

When a user upgrades, bonus generation credits are granted with a 30-day expiry:

| Plan | Credits Granted |
|---|---|
| Starter | 50 |
| Pro | 200 |
| Business | 1,000 |
| Enterprise | Negotiated |

---

## Trial Periods

To activate a trial:

```
POST /api/v1/billing/checkout
{ "plan_name": "pro", "trial_days": 14, ... }
```

The `trial_ends_at` timestamp is stored on the subscription.  Quotas are enforced at the trial plan level.  When the trial ends and no payment method is on file, the subscription downgrades to Free.
