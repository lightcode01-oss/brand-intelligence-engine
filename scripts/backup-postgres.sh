#!/usr/bin/env bash
# =============================================================================
# Nomen — PostgreSQL Backup Script
# Usage: ./backup-postgres.sh [environment]
# Requires: pg_dump, gzip, aws CLI (for S3 upload)
# =============================================================================

set -euo pipefail

# ---- Configuration ----
ENVIRONMENT="${1:-production}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_DIR:-/var/backups/nomen}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-}"
DATABASE_URL="${DATABASE_URL:-}"

# Parse DATABASE_URL into components
if [[ -z "$DATABASE_URL" ]]; then
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"
    DB_NAME="${DB_NAME:-nomen_db}"
    DB_USER="${DB_USER:-nomen_user}"
    DB_PASSWORD="${DB_PASSWORD:-}"
else
    # Parse postgresql+asyncpg://user:pass@host:port/db
    CLEAN_URL="${DATABASE_URL/postgresql+asyncpg:\/\//postgresql:\/\/}"
    DB_USER=$(echo "$CLEAN_URL" | sed 's/postgresql:\/\/\([^:]*\):.*/\1/')
    DB_PASSWORD=$(echo "$CLEAN_URL" | sed 's/postgresql:\/\/[^:]*:\([^@]*\)@.*/\1/')
    DB_HOST=$(echo "$CLEAN_URL" | sed 's/postgresql:\/\/[^@]*@\([^:\/]*\).*/\1/')
    DB_PORT=$(echo "$CLEAN_URL" | sed 's/postgresql:\/\/[^@]*@[^:]*:\([0-9]*\)\/.*/\1/')
    DB_NAME=$(echo "$CLEAN_URL" | sed 's/.*\/\([^?]*\).*/\1/')
fi

BACKUP_FILE="nomen_${ENVIRONMENT}_${TIMESTAMP}.sql.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

# ---- Setup ----
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting PostgreSQL backup"
echo "  Environment: $ENVIRONMENT"
echo "  Database: $DB_NAME @ $DB_HOST:$DB_PORT"
echo "  Output: $BACKUP_PATH"

mkdir -p "$BACKUP_DIR"

# ---- Run pg_dump ----
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Running pg_dump..."
PGPASSWORD="$DB_PASSWORD" pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --format=plain \
    --no-password \
    --verbose \
    2>&1 | gzip > "$BACKUP_PATH"

BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Backup complete: ${BACKUP_FILE} (${BACKUP_SIZE})"

# ---- Upload to S3 (if configured) ----
if [[ -n "$S3_BUCKET" ]]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Uploading to S3: s3://${S3_BUCKET}/backups/${BACKUP_FILE}"
    aws s3 cp "$BACKUP_PATH" "s3://${S3_BUCKET}/backups/${BACKUP_FILE}" \
        --storage-class STANDARD_IA \
        --sse AES256
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] S3 upload complete"
fi

# ---- Local retention cleanup ----
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Cleaning up backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "nomen_*.sql.gz" -mtime "+${RETENTION_DAYS}" -delete
REMAINING=$(find "$BACKUP_DIR" -name "nomen_*.sql.gz" | wc -l)
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Backup retention: ${REMAINING} files remaining"

# ---- S3 lifecycle cleanup ----
if [[ -n "$S3_BUCKET" ]]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Note: S3 lifecycle policy handles remote retention automatically"
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Backup job finished successfully"
exit 0
