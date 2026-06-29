import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Optional, Any
from app.core.config import settings

def base64url_encode(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("utf-8")

def base64url_decode(payload: str) -> bytes:
    padding = "=" * (4 - (len(payload) % 4))
    return base64.urlsafe_b64decode(payload + padding)

class JWTError(Exception):
    pass

class ExpiredSignatureError(JWTError):
    pass

def encode_jwt(payload: dict[str, Any], secret: str = settings.SECRET_KEY, expires_in: int = 900) -> str:
    """Encodes a payload dict into a valid HS256 JWT string."""
    header = {"alg": "HS256", "typ": "JWT"}
    
    # Inject expiration
    full_payload = payload.copy()
    full_payload["exp"] = int(time.time()) + expires_in
    full_payload["iat"] = int(time.time())
    
    header_json = json.dumps(header, separators=(",", ":")).encode("utf-8")
    payload_json = json.dumps(full_payload, separators=(",", ":")).encode("utf-8")
    
    encoded_header = base64url_encode(header_json)
    encoded_payload = base64url_encode(payload_json)
    
    signature_base = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signature_base, hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)
    
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def decode_jwt(token: str, secret: str = settings.SECRET_KEY) -> dict[str, Any]:
    """Decodes and verifies a JWT string, raising JWTError if invalid or expired."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise JWTError("Invalid token format.")
            
        encoded_header, encoded_payload, encoded_signature = parts
        
        # Verify signature
        signature_base = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), signature_base, hashlib.sha256).digest()
        actual_sig = base64url_decode(encoded_signature)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise JWTError("Invalid signature.")
            
        # Decode payload
        payload_data = json.loads(base64url_decode(encoded_payload).decode("utf-8"))
        
        # Verify expiration
        if "exp" in payload_data and time.time() > payload_data["exp"]:
            raise ExpiredSignatureError("Token has expired.")
            
        return payload_data
    except ExpiredSignatureError:
        raise
    except Exception as exc:
        raise JWTError(f"Token decoding failed: {str(exc)}")
