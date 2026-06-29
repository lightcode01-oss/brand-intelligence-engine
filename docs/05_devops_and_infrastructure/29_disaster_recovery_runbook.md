# Disaster Recovery Runbook: Nomen

This guide outlines database backup automation, system recovery sequences, and incident response scenarios.

---

## 1. Database Backup & Restore Guide

### 1.1. PostgreSQL Automated Backups
Run this script via cron every night to write a compressed schema and data dump file to storage:

```bash
#!/bin/bash
# pg_backup.sh
BACKUP_DIR="/opt/backups/postgres"
DATE=$(date +\%Y-\%m-\%d_\%H-\%m-\%s)
FILENAME="nomen_prod_$DATE.sql.gz"

echo "Starting PostgreSQL backup..."
pg_dump -h nomen-postgres -U nomen_user -d nomen_db -F c | gzip > "$BACKUP_DIR/$FILENAME"
echo "Backup saved to $BACKUP_DIR/$FILENAME"
```

### 1.2. Restoring PostgreSQL Dump
To restore a backup dump in the event of database volume corruption:

```bash
# 1. Terminate active sessions and drop database
dropdb -h nomen-postgres -U nomen_user nomen_db

# 2. Re-create empty target database
createdb -h nomen-postgres -U nomen_user nomen_db

# 3. Restore dump
gunzip -c /opt/backups/postgres/nomen_prod_backup_file.sql.gz | pg_restore -h nomen-postgres -U nomen_user -d nomen_db
```

---

## 2. Redis Caching Persistence

Redis is configured to persist keys to disk using RDB snapshotting.
- **Location**: Volume `/data/dump.rdb` inside the Redis container.
- **Backup**: Copy the `dump.rdb` file every 2 hours to a secure secondary volume.
- **Recovery**: Stop Redis service, copy the backup `dump.rdb` to the `/data` folder, and restart Redis.

---

## 3. Incident Scenarios & Response Runbooks

### 3.1. Scenario: Database Volume Corruption
- **Symptom**: Database server crash or read-only volume error.
- **Response**:
  1. Set Maintenance Mode toggle to `True` in config Map (sends 503 Service Unavailable to users).
  2. Provision a new Postgres StatefulSet pod.
  3. Run the database restore script from the latest nightly dump.
  4. Run Alembic upgrade checks: `alembic upgrade head`.
  5. Disable Maintenance Mode.

### 3.2. Scenario: AI Provider Throttling / API Keys Exhausted
- **Symptom**: Generated names pipeline returning "Out of quota" or "429 Too Many Requests" from OpenAI/Gemini.
- **Response**:
  1. Our Registry implements provider fallback automatically. If Gemini fails, it queries OpenAI next.
  2. If all cloud providers fail, the registry falls back to the local `Ollama` endpoint.
  3. Verify API keys limits in developers portals, renew billing details, or swap key entries in Kubernetes secrets.
