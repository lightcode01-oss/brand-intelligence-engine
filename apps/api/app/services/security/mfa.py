"""MFA service: TOTP device registration, verification, and recovery codes."""
import uuid
import hmac
import hashlib
import secrets
import base64
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.security import MFADevice, RecoveryCode

# TOTP window tolerance: ±1 step (30s window * 2 = 90s grace)
_TOTP_DIGITS = 6
_TOTP_PERIOD = 30
_RECOVERY_CODE_LENGTH = 16
_RECOVERY_CODE_COUNT = 10


def _generate_totp_secret() -> str:
    """Generate a 20-byte random secret encoded as base32."""
    raw = secrets.token_bytes(20)
    return base64.b32encode(raw).decode("utf-8")


def _hotp(secret_b32: str, counter: int) -> int:
    """Compute an HOTP value using HMAC-SHA1."""
    key = base64.b32decode(secret_b32.upper())
    msg = counter.to_bytes(8, "big")
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    code = (
        (h[offset] & 0x7F) << 24
        | h[offset + 1] << 16
        | h[offset + 2] << 8
        | h[offset + 3]
    )
    return code % (10 ** _TOTP_DIGITS)


def _current_totp(secret_b32: str) -> list[int]:
    """Return valid codes for current, previous, and next TOTP windows."""
    ts = int(datetime.now(timezone.utc).timestamp())
    step = ts // _TOTP_PERIOD
    return [_hotp(secret_b32, step - 1), _hotp(secret_b32, step), _hotp(secret_b32, step + 1)]


def _hash_code(code: str) -> str:
    """One-way hash for recovery code storage."""
    return hashlib.sha256(code.encode()).hexdigest()


class MFAService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def provision_totp(self, user_id: uuid.UUID) -> dict:
        """Create an unverified TOTP device and return the OTP URI for QR code generation."""
        secret = _generate_totp_secret()
        # In production, encrypt secret before storage. Here we store base32 directly.
        device = MFADevice(
            user_id=user_id,
            method="TOTP",
            secret_encrypted=secret,
            is_verified=False,
            is_primary=False,
        )
        self.db.add(device)
        await self.db.flush()
        otp_uri = (
            f"otpauth://totp/Nomen%3A{user_id}?secret={secret}&issuer=Nomen&digits={_TOTP_DIGITS}&period={_TOTP_PERIOD}"
        )
        return {"device_id": str(device.id), "secret": secret, "otp_uri": otp_uri}

    async def verify_and_activate(self, user_id: uuid.UUID, device_id: uuid.UUID, code: str) -> dict:
        """Verify a TOTP code during setup and mark the device as verified."""
        result = await self.db.execute(
            select(MFADevice).where(MFADevice.id == device_id, MFADevice.user_id == user_id)
        )
        device = result.scalar_one_or_none()
        if not device:
            return {"success": False, "error": "MFA device not found."}

        valid_codes = [str(c).zfill(_TOTP_DIGITS) for c in _current_totp(device.secret_encrypted)]
        if code not in valid_codes:
            return {"success": False, "error": "Invalid TOTP code."}

        device.is_verified = True
        device.is_primary = True
        device.last_used_at = datetime.now(timezone.utc)

        # Generate recovery codes
        recovery_codes = [secrets.token_hex(8) for _ in range(_RECOVERY_CODE_COUNT)]
        for rc in recovery_codes:
            self.db.add(RecoveryCode(
                user_id=user_id,
                mfa_device_id=device.id,
                code_hash=_hash_code(rc),
                is_used=False,
            ))

        device.backup_codes_generated = True
        await self.db.flush()
        return {"success": True, "recovery_codes": recovery_codes}

    async def verify_totp_code(self, user_id: uuid.UUID, code: str) -> bool:
        """Validate a TOTP code for an authenticated user. Returns True on success."""
        result = await self.db.execute(
            select(MFADevice).where(
                MFADevice.user_id == user_id,
                MFADevice.is_verified == True,
                MFADevice.is_primary == True
            )
        )
        device = result.scalar_one_or_none()
        if not device:
            return False

        valid_codes = [str(c).zfill(_TOTP_DIGITS) for c in _current_totp(device.secret_encrypted)]
        if code in valid_codes:
            device.last_used_at = datetime.now(timezone.utc)
            await self.db.flush()
            return True
        return False

    async def verify_recovery_code(self, user_id: uuid.UUID, code: str) -> bool:
        """Consume a single-use recovery code. Returns True on success."""
        code_hash = _hash_code(code)
        result = await self.db.execute(
            select(RecoveryCode).where(
                RecoveryCode.user_id == user_id,
                RecoveryCode.code_hash == code_hash,
                RecoveryCode.is_used == False
            )
        )
        rc = result.scalar_one_or_none()
        if not rc:
            return False
        rc.is_used = True
        rc.used_at = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    async def disable_mfa(self, user_id: uuid.UUID) -> bool:
        """Remove the primary MFA device for a user."""
        result = await self.db.execute(
            select(MFADevice).where(MFADevice.user_id == user_id, MFADevice.is_primary == True)
        )
        device = result.scalar_one_or_none()
        if not device:
            return False
        device.is_verified = False
        device.is_primary = False
        await self.db.flush()
        return True

    async def get_device_status(self, user_id: uuid.UUID) -> dict:
        """Return MFA enrollment status for a user."""
        result = await self.db.execute(
            select(MFADevice).where(MFADevice.user_id == user_id, MFADevice.is_primary == True)
        )
        device = result.scalar_one_or_none()
        return {
            "enabled": device is not None and device.is_verified,
            "method": device.method if device else None,
            "device_name": device.name if device else None,
            "last_used_at": device.last_used_at.isoformat() if device and device.last_used_at else None,
        }

    async def list_recovery_codes(self, user_id: uuid.UUID) -> dict:
        """Return the count of remaining valid recovery codes."""
        result = await self.db.execute(
            select(RecoveryCode).where(
                RecoveryCode.user_id == user_id,
                RecoveryCode.is_used == False
            )
        )
        remaining = result.scalars().all()
        return {"remaining_count": len(remaining)}
