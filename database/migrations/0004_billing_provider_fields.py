"""
Migration 0004: Add billing provider fields to subscription and related tables.

Adds:
  - subscriptions.gateway_subscription_id  (provider-side subscription ID)
  - subscriptions.gateway_customer_id      (provider-side customer ID)
  - subscriptions.provider                 (billing provider slug)
  - subscriptions.plan_name               (human-readable plan name)
  - subscriptions.trial_ends_at           (trial end timestamp)
  - webhook_events.idempotency_key        (unique dedup key)
  - plans seed data                        (free, starter, pro, business, enterprise)
"""

from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

UPGRADE_SQL = """
-- Add provider columns to subscriptions
ALTER TABLE subscriptions
    ADD COLUMN IF NOT EXISTS gateway_subscription_id VARCHAR(255),
    ADD COLUMN IF NOT EXISTS gateway_customer_id     VARCHAR(255),
    ADD COLUMN IF NOT EXISTS provider                VARCHAR(50) DEFAULT 'stripe',
    ADD COLUMN IF NOT EXISTS plan_name               VARCHAR(100),
    ADD COLUMN IF NOT EXISTS trial_ends_at           TIMESTAMPTZ;

-- Add idempotency key to webhook_events for deduplication
ALTER TABLE webhook_events
    ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(500) UNIQUE;

-- Create index for fast webhook dedup lookups
CREATE INDEX IF NOT EXISTS idx_webhook_events_idempotency
    ON webhook_events (idempotency_key)
    WHERE idempotency_key IS NOT NULL;

-- Create index on gateway_customer_id for portal lookups
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer_id
    ON subscriptions (gateway_customer_id)
    WHERE gateway_customer_id IS NOT NULL;

-- Seed pricing plans (upsert to support re-runs)
INSERT INTO plans (id, name, price_monthly, limits_json, features_json, created_at, updated_at)
VALUES
    (gen_random_uuid(), 'free', 0.0,
        '{"generations_per_month": 10, "exports_per_month": 5, "api_requests_per_month": 100, "workspaces": 1, "projects_per_workspace": 3, "team_members": 1}'::jsonb,
        '{"ai_providers": ["gemini"], "bulk_generation": false, "priority_support": false, "custom_domain_check": false, "trademark_analysis": false, "logo_recommendations": false}'::jsonb,
        NOW(), NOW()),
    (gen_random_uuid(), 'starter', 9.0,
        '{"generations_per_month": 100, "exports_per_month": 50, "api_requests_per_month": 1000, "workspaces": 2, "projects_per_workspace": 10, "team_members": 3}'::jsonb,
        '{"ai_providers": ["gemini", "openai"], "bulk_generation": true, "priority_support": false, "custom_domain_check": true, "trademark_analysis": false, "logo_recommendations": false}'::jsonb,
        NOW(), NOW()),
    (gen_random_uuid(), 'pro', 29.0,
        '{"generations_per_month": 500, "exports_per_month": 200, "api_requests_per_month": 10000, "workspaces": 5, "projects_per_workspace": 50, "team_members": 10}'::jsonb,
        '{"ai_providers": ["gemini", "openai", "claude"], "bulk_generation": true, "priority_support": true, "custom_domain_check": true, "trademark_analysis": true, "logo_recommendations": true}'::jsonb,
        NOW(), NOW()),
    (gen_random_uuid(), 'business', 99.0,
        '{"generations_per_month": 2000, "exports_per_month": 1000, "api_requests_per_month": 50000, "workspaces": 20, "projects_per_workspace": 200, "team_members": 50}'::jsonb,
        '{"ai_providers": ["gemini", "openai", "claude", "ollama"], "bulk_generation": true, "priority_support": true, "custom_domain_check": true, "trademark_analysis": true, "logo_recommendations": true}'::jsonb,
        NOW(), NOW()),
    (gen_random_uuid(), 'enterprise', 0.0,
        '{"generations_per_month": -1, "exports_per_month": -1, "api_requests_per_month": -1, "workspaces": -1, "projects_per_workspace": -1, "team_members": -1}'::jsonb,
        '{"ai_providers": ["gemini", "openai", "claude", "ollama"], "bulk_generation": true, "priority_support": true, "custom_domain_check": true, "trademark_analysis": true, "logo_recommendations": true, "sso": true, "audit_logs": true, "custom_ai_models": true}'::jsonb,
        NOW(), NOW())
ON CONFLICT (name) DO UPDATE
    SET price_monthly  = EXCLUDED.price_monthly,
        limits_json    = EXCLUDED.limits_json,
        features_json  = EXCLUDED.features_json,
        updated_at     = NOW();
"""

# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------

DOWNGRADE_SQL = """
-- Remove provider columns from subscriptions
ALTER TABLE subscriptions
    DROP COLUMN IF EXISTS gateway_subscription_id,
    DROP COLUMN IF EXISTS gateway_customer_id,
    DROP COLUMN IF EXISTS provider,
    DROP COLUMN IF EXISTS plan_name,
    DROP COLUMN IF EXISTS trial_ends_at;

-- Remove idempotency key from webhook_events
DROP INDEX IF EXISTS idx_webhook_events_idempotency;
ALTER TABLE webhook_events DROP COLUMN IF EXISTS idempotency_key;

DROP INDEX IF EXISTS idx_subscriptions_customer_id;

-- Remove plan seeds
DELETE FROM plans WHERE name IN ('free', 'starter', 'pro', 'business', 'enterprise');
"""


def upgrade(connection) -> None:
    """Apply migration 0004."""
    connection.execute(UPGRADE_SQL)
    print("[0004] Billing provider fields and plan seeds applied.")


def downgrade(connection) -> None:
    """Revert migration 0004."""
    connection.execute(DOWNGRADE_SQL)
    print("[0004] Billing provider fields and plan seeds reverted.")
