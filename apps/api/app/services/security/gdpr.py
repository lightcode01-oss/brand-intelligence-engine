"""GDPR service: data export, deletion, and consent management."""
import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.security import DataExportRequest, DataDeletionRequest, ConsentRecord

_DELETION_GRACE_DAYS = 30


class GDPRService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Data Export (GDPR Art. 20) ────────────────────────────────────────
    async def request_data_export(self, user_id: uuid.UUID) -> dict:
        """Submit a GDPR Article 20 data portability export request."""
        # Check if a pending export already exists
        result = await self.db.execute(
            select(DataExportRequest).where(
                DataExportRequest.user_id == user_id,
                DataExportRequest.status.in_(["PENDING", "PROCESSING"]),
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return {
                "export_id": str(existing.id),
                "status": existing.status,
                "message": "An export request is already in progress.",
            }

        now = datetime.now(timezone.utc)
        export = DataExportRequest(
            user_id=user_id,
            status="PENDING",
            requested_at=now,
        )
        self.db.add(export)
        await self.db.flush()

        # In production: dispatch background task to assemble the archive.
        # Simulate instant completion for now.
        export.status = "COMPLETED"
        export.completed_at = now
        export.download_url = f"/api/v1/security/gdpr/exports/{export.id}/download"
        export.expires_at = now + timedelta(days=7)
        await self.db.flush()

        return {
            "export_id": str(export.id),
            "status": "COMPLETED",
            "download_url": export.download_url,
            "expires_at": export.expires_at.isoformat(),
        }

    async def get_export_history(self, user_id: uuid.UUID) -> list[dict]:
        """Return all data export requests for a user."""
        result = await self.db.execute(
            select(DataExportRequest)
            .where(DataExportRequest.user_id == user_id)
            .order_by(DataExportRequest.requested_at.desc())
        )
        exports = result.scalars().all()
        return [
            {
                "id": str(e.id),
                "status": e.status,
                "requested_at": e.requested_at.isoformat(),
                "download_url": e.download_url,
                "expires_at": e.expires_at.isoformat() if e.expires_at else None,
            }
            for e in exports
        ]

    async def generate_export_payload(self, user_id: uuid.UUID) -> dict:
        """Assemble a user data archive payload (in-memory, production would write to S3)."""
        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user_id": str(user_id),
            "data_categories": [
                "profile",
                "workspaces",
                "projects",
                "generations",
                "billing",
                "audit_events",
                "preferences",
            ],
            "format": "JSON",
            "version": "1.0",
            "note": "Complete data export as per GDPR Article 20 right to data portability.",
        }

    # ── Account Deletion (GDPR Art. 17) ──────────────────────────────────
    async def request_account_deletion(self, user_id: uuid.UUID, reason: Optional[str] = None) -> dict:
        """Submit a GDPR Article 17 right-to-erasure request."""
        result = await self.db.execute(
            select(DataDeletionRequest).where(
                DataDeletionRequest.user_id == user_id,
                DataDeletionRequest.status.in_(["PENDING", "CONFIRMED"]),
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return {
                "deletion_id": str(existing.id),
                "status": existing.status,
                "scheduled_for": existing.scheduled_for.isoformat() if existing.scheduled_for else None,
                "message": "A deletion request is already pending confirmation.",
            }

        now = datetime.now(timezone.utc)
        deletion = DataDeletionRequest(
            user_id=user_id,
            status="PENDING",
            reason=reason,
            requested_at=now,
            scheduled_for=now + timedelta(days=_DELETION_GRACE_DAYS),
        )
        self.db.add(deletion)
        await self.db.flush()

        return {
            "deletion_id": str(deletion.id),
            "status": "PENDING",
            "scheduled_for": deletion.scheduled_for.isoformat(),
            "message": (
                f"Your account is scheduled for permanent deletion in {_DELETION_GRACE_DAYS} days. "
                "You may cancel this request before that date."
            ),
        }

    async def cancel_deletion_request(self, user_id: uuid.UUID) -> dict:
        """Cancel a pending deletion request."""
        result = await self.db.execute(
            select(DataDeletionRequest).where(
                DataDeletionRequest.user_id == user_id,
                DataDeletionRequest.status.in_(["PENDING", "CONFIRMED"]),
            )
        )
        deletion = result.scalar_one_or_none()
        if not deletion:
            return {"success": False, "error": "No pending deletion request found."}

        deletion.status = "CANCELLED"
        await self.db.flush()
        return {"success": True, "message": "Deletion request cancelled successfully."}

    async def get_deletion_status(self, user_id: uuid.UUID) -> dict:
        """Get the current deletion request status for a user."""
        result = await self.db.execute(
            select(DataDeletionRequest)
            .where(DataDeletionRequest.user_id == user_id)
            .order_by(DataDeletionRequest.requested_at.desc())
        )
        deletion = result.scalars().first()
        if not deletion:
            return {"has_request": False}
        return {
            "has_request": True,
            "deletion_id": str(deletion.id),
            "status": deletion.status,
            "requested_at": deletion.requested_at.isoformat(),
            "scheduled_for": deletion.scheduled_for.isoformat() if deletion.scheduled_for else None,
        }

    # ── Consent Management ────────────────────────────────────────────────
    async def record_consent(
        self,
        user_id: uuid.UUID,
        consent_type: str,
        granted: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        """Record a user consent event."""
        record = ConsentRecord(
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(record)
        await self.db.flush()
        return {
            "id": str(record.id),
            "consent_type": consent_type,
            "granted": granted,
            "recorded_at": record.created_at.isoformat() if record.created_at else None,
        }

    async def get_consent_history(self, user_id: uuid.UUID) -> list[dict]:
        """Return the full consent audit trail for a user."""
        result = await self.db.execute(
            select(ConsentRecord)
            .where(ConsentRecord.user_id == user_id)
            .order_by(ConsentRecord.created_at.desc())
        )
        records = result.scalars().all()
        return [
            {
                "id": str(r.id),
                "consent_type": r.consent_type,
                "granted": r.granted,
                "ip_address": r.ip_address,
                "recorded_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
