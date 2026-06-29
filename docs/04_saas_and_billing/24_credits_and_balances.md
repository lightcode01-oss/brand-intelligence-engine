# Token Credits & Balances: Nomen

This guide details the Credit Engine, transaction ledgers, concurrency locking, and refunds logic.

---

## 1. Credit Calculations

Nomen supports a virtual token credit system. User balance is calculated dynamically by summing active transactions:

$$\text{Active Balance} = \sum (\text{CREDIT} + \text{REFUND}) - \sum (\text{DEBIT})$$

- Excludes any `CREDIT` row where `expires_at` has passed.
- Excludes any transaction flagged as deleted (`deleted_at != None`).

---

## 2. Concurrency Control (Atomic Debits)

To prevent race conditions (such as a developer sending 50 parallel API generation requests simultaneously to consume a remaining 1-credit balance), the Credit Engine utilizes **pessimistic locking** during debit operations:

```python
# Atomic credit debit lock logic
stmt = select(User).where(User.id == user_id).with_for_update()
user = (await db.execute(stmt)).scalar()
# Recalculate balance and write DEBIT row inside transaction block
```

This guarantees that database operations are serialized per user, preventing double-spending or negative balances.

---

## 3. Credit Expiration Sweeper

A Celery scheduler task (`expire_outdated_credits`) runs hourly to check for expired credits. It:
1. Identifies `CREDIT` rows where `expires_at < now` and `used_at == None`.
2. Marks `used_at` to the expiration time, invalidating them from future balance summaries.
