# Customer Portal

## Overview

The customer portal is a provider-hosted page that allows users to:

- Update payment methods
- View and download past invoices
- Manage active subscriptions
- Update billing address and tax information

---

## Launching the Portal

### API

```
POST /api/v1/billing/portal
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "return_url": "https://app.nomen.ai/billing",
  "provider": "stripe"           // optional — defaults to primary
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "portal_url": "https://billing.stripe.com/session/xxx",
    "provider": "stripe"
  }
}
```

Redirect the user to `portal_url`. The session expires after 5 minutes.

### Frontend

The dashboard billing page includes a "Manage Subscription" button that calls this endpoint and performs a `window.location.href` redirect.

---

## Provider Differences

### Stripe

- Full self-service portal powered by [Stripe Customer Portal](https://stripe.com/docs/customer-management).
- Supports: payment method updates, subscription management, invoice downloads, cancellation.
- Session expires in 5 minutes.
- **Setup required**: Enable the Customer Portal in the Stripe dashboard and configure allowed actions.

### Lemon Squeezy

- No API-driven portal session.
- Users are redirected to `https://app.lemonsqueezy.com/my-orders`.
- Customers can manage subscriptions from their LS dashboard.
- **Limitation**: Does not support payment method updates through the Nomen portal flow.

---

## Security Considerations

- Portal sessions are **single-use** and short-lived (Stripe: 5 min TTL).
- The `return_url` must be an allowed domain registered in your provider dashboard.
- Never expose raw portal URLs in logs — they grant direct billing access.
- The portal endpoint requires an authenticated JWT — unauthenticated users cannot access it.

---

## Stripe Customer Portal Configuration

1. Go to **Stripe Dashboard → Settings → Billing → Customer portal**
2. Enable the following:
   - Update payment methods
   - Cancel subscriptions
   - Invoice history
3. Add `https://app.nomen.ai` to allowed return URLs
4. (Optional) Add your brand logo and colors
