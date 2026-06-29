# Payment Gateways — Architecture & Integration

## Overview

Nomen integrates two payment gateways through a provider-agnostic abstraction layer:

| Provider | Type | Priority |
|---|---|---|
| **Stripe** | Primary | Configured in `BILLING_PROVIDER=stripe` |
| **Lemon Squeezy** | Secondary | Configured in `BILLING_PROVIDER_FALLBACK=lemonsqueezy` |

All gateway logic is isolated behind `AbstractPaymentProvider` and never leaks into service or API layers.

---

## Architecture

```
apps/api/app/services/billing/
├── providers/
│   ├── base.py           ← AbstractPaymentProvider + typed dataclasses
│   ├── stripe.py         ← Stripe SDK wrapper
│   ├── lemonsqueezy.py   ← LemonSqueezy REST API (httpx)
│   └── registry.py       ← Provider registry singleton
├── subscription_service.py
├── plan_service.py
├── invoice_service.py
├── coupon_service.py
└── usage_service.py
```

---

## Configuration

Add the following to your `.env`:

```env
# Primary gateway
BILLING_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_IDS={"starter": "price_xxx", "pro": "price_yyy", "business": "price_zzz"}

# Secondary gateway (optional)
BILLING_PROVIDER_FALLBACK=lemonsqueezy
LEMONSQUEEZY_API_KEY=your_api_key
LEMONSQUEEZY_STORE_ID=12345
LEMONSQUEEZY_WEBHOOK_SECRET=your_webhook_secret
LEMONSQUEEZY_VARIANT_IDS={"starter": "111111", "pro": "222222", "business": "333333"}
```

---

## Adding a New Payment Gateway

1. Create `apps/api/app/services/billing/providers/myprovider.py`
2. Subclass `AbstractPaymentProvider` and implement all abstract methods
3. Add an entry to `_PROVIDER_MAP` in `registry.py`:
   ```python
   _PROVIDER_MAP["myprovider"] = "app.services.billing.providers.myprovider.MyProvider"
   ```
4. Set `BILLING_PROVIDER=myprovider` in `.env`

No other code changes required.

---

## Stripe Provider

The Stripe provider uses the official `stripe` Python SDK.

### Key behaviours

- **Customer registration**: Searches by `metadata.nomen_user_id` before creating. Idempotency key prevents duplicate customers.
- **Checkout**: Uses Stripe Checkout Sessions in `subscription` mode.
- **Proration**: Upgrades use `proration_behavior=always_invoice` (immediate debit). Downgrades use `none` (applied at renewal).
- **Cancellation**: Default is `cancel_at_period_end=True` (access retained until period ends). `immediate=True` deletes instantly.
- **Webhook verification**: Uses `stripe.Webhook.construct_event` with `STRIPE_WEBHOOK_SECRET`.

### Required Stripe dashboard setup

1. Create products and prices for each plan
2. Add price IDs to `STRIPE_PRICE_IDS`
3. Configure webhook endpoint: `POST /api/v1/webhooks/stripe`
4. Enable events: `checkout.session.completed`, `customer.subscription.*`, `invoice.*`, `charge.refunded`

---

## Lemon Squeezy Provider

The LemonSqueezy provider uses `httpx` — no SDK dependency.

### Key behaviours

- **Customer registration**: LemonSqueezy creates customers implicitly on checkout completion. The `create_customer` call returns a virtual tag for pre-fill purposes.
- **Checkout**: Uses the Checkouts API. `custom.nomen_user_id` is passed in `checkout_data` for webhook correlation.
- **Plan change**: Both upgrades and downgrades use the same PATCH `/subscriptions/{id}` call. Lemon Squeezy always applies at renewal.
- **Webhook verification**: HMAC-SHA256 computed over the raw body, compared against `X-Signature`.
- **Customer portal**: No API-driven portal. Returns the static `app.lemonsqueezy.com/my-orders` URL.

### Required Lemon Squeezy dashboard setup

1. Create a store and products with variants per plan
2. Add variant IDs to `LEMONSQUEEZY_VARIANT_IDS`
3. Configure webhook endpoint: `POST /api/v1/webhooks/lemonsqueezy`
4. Enable all subscription and order events
