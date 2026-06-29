#!/usr/bin/env bash
# =============================================================================
# Nomen — PostgreSQL Restore Script
# Usage: ./restore-postgres.sh <backup_file_or_s3_uri> [environment]
# =============================================================================

set -euo pipefail

BACKUP_SOURCE="${1:-}"
ENVIRONMENT="${2:-production}"

if [[ -z "$BACKUP_SOURCE" ]]; then
    echo "Usage: $0 <backup_file_or_s3_uri> [environment]"
    echo "Example: $0 /var/backups/nomen/nomen_production_20260101_120000.sql.gz"
    echo "Example: $0 s3://my-bucket/backups/nomen_production_20260101_120000.sql.gz"
    exit 1
fi

# ---- Configuration ----
DATABASE_URL="${DATABASE_URL:-}"
CONFIRM="${CONFIRM:-no}"

if [[ -z "$DATABASE_URL" ]]; then
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"
    DB_NAME="${DB_NAME:-nomen_db}"
    DB_USER="${DB_USER:-nomen_user}"
    DB_PASSWORD="${DB_PASSWORD:-}"
else
    CLEAN_URL="${DATABASE_URL/postgresql+asyncpg:\/\//postgresql:\/\/}"
    DB_USER=$(echo "$CLEAN_URL" | sed 's/postgresql:\/\/\([^:]*\):.*/\1/')
    DB_PASSWORD=$(echo "$CLEAN_URL" | sed 's/postgresql:\/\/[^:]*:\([^@]*\)@.*/\1/')
    DB_HOST=$(echo "$CLEAN_URL" | sed 's/postgresql:\/\/[^@]*@\([^:\/]*\).*/\1/')
    DB_PORT=$(echo "$CLEAN_URL" | sed 's/postgresql:\/\/[^@]*@[^:]*:\([0-9]*\)\/.*/\1/')
    DB_NAME=$(echo "$CLEAN_URL" | sed 's/.*\/\([^?]*\).*/\1/')
fi

# ---- Safety confirmation ----
echo "⚠️  WARNING: This will OVERWRITE the database: ${DB_NAME} @ ${DB_HOST}:${DB_PORT}"
echo "   Environment: $ENVIRONMENT"
echo "   Source: $BACKUP_SOURCE"
echo ""

if [[ "$CONFIRM" != "yes" ]]; then
    read -r -p "Type 'yes' to continue: " USER_CONFIRM
    if [[ "$USER_CONFIRM" != "yes" ]]; then
        echo "Restore cancelled."
        exit 0
    fi
fi

# ---- Download from S3 if needed ----
LOCAL_FILE="$BACKUP_SOURCE"
if [[ "$BACKUP_SOURCE" == s3://* ]]; then
    LOCAL_FILE="/tmp/restore_$(date +%s).sql.gz"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Downloading from S3..."
    aws s3 cp "$BACKUP_SOURCE" "$LOCAL_FILE"
fi

# ---- Restore ----
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting restore from: $LOCAL_FILE"

# Drop existing connections
PGPASSWORD="$DB_PASSWORD" psql \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="postgres" \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();" \
    || true

# Restore
gunzip -c "$LOCAL_FILE" | PGPASSWORD="$DB_PASSWORD" psql \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Restore complete"

# Cleanup temp file
if [[ "$BACKUP_SOURCE" == s3://* ]]; then
    rm -f "$LOCAL_FILE"
fi

exit 0
