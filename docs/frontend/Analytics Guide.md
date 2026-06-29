# Analytics and Newsletter Provider Integrations

## Analytics Provider Abstraction

Nomen implements an environment-driven analytics wrapper inside `src/lib/analytics.ts` and `src/components/analytics/AnalyticsProvider.tsx`.

We support the following tracking tools, selected via environment variables:

| Value | Script Loaded | Initializer / Call |
|---|---|---|
| `ga` | Google Tag Manager script | Triggers standard `gtag('event')` payloads |
| `plausible` | Plausible.io script | Triggers custom `plausible()` tracker functions |
| `posthog` | PostHog script | Triggers custom `posthog.capture()` actions |
| `none` / empty | None (Developer logs) | Console debug tracking |

### Usage

```typescript
import { track } from '@/lib/analytics';

track('checkout_completed', { plan: 'pro', value: 29.00 });
```

## Newsletter Provider Abstraction

Subscribing user emails is centralized in `src/lib/newsletter.ts` and handled by the `/api/newsletter/subscribe` Route Handler:

We support the following providers via `.env` configuration:

1. **Mailchimp**: Integrates through the official API v3 list members endpoint.
2. **ConvertKit**: Integrates using the standard ConvertKit form subscriber endpoint.
3. **Resend**: Integrates contacts into the Resend Audience Contacts API database.
4. **Mock**: Logs subscriptions in development to prevent API lockouts.
