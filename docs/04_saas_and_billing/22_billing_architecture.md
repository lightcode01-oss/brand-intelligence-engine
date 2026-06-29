# SaaS Billing Architecture: Nomen

This document outlines Nomen's provider-agnostic billing foundation, subscription structures, and atomic ledger models.

---

## 1. Domain Entities & Database Mapping

Our billing database schemas track plans, coupons, subscriptions, invoices, and credits:

- **`plans`**: Configuration limits matrix (workspaces, projects count) and active feature flag flags (AI Providers, Bulk generation, custom domains, White-labeling).
- **`subscriptions`**: The client's active billing contract. Points to a specific pricing tier, tracks billing cycles, resets counters, and locks status.
- **`invoices`**: Billing records containing totals, transaction currency, statuses (`PAID`, `OPEN`, `VOID`), and raw gateway payload blobs.
- **`coupons`**: Discount codes setting promotional percentages (e.g. `20% off`).
- **`webhook_events`**: Stores raw incoming payment events log to retry and audit webhook transactions.

---

## 2. Dynamic Provider Abstraction

Nomen decouples all operations from specific gateways (e.g., Stripe, Paddle, Razorpay) by defining `AbstractBillingService`:

```python
class AbstractBillingService(ABC):
    @abstractmethod
    async def create_customer(self, user_id: uuid.UUID, email: str) -> str: pass
    @abstractmethod
    async def create_checkout_session(self, user_id: uuid.UUID, plan_name: str, cancel_url: str, success_url: str) -> str: pass
    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> bool: pass
```

This dynamic registry allows deploying Paddle in EU regions, Stripe in US markets, and local providers without altering core database entities or domain code.
