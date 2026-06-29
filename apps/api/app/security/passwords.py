import hashlib
import os
import secrets
from typing import Tuple

try:
    from argon2 import PasswordHasher
    ph = PasswordHasher()
except ImportError:
    ph = None

# Custom PBKDF2 parameters for fallback
ITERATIONS = 100000
HASH_NAME = "sha256"

def hash_password(password: str) -> str:
    """Hashes a plaintext password using Argon2id, falling back to PBKDF2-SHA256 if uninstalled."""
    if ph:
        return ph.hash(password)
    
    # Secure PBKDF2 Fallback
    salt = secrets.token_bytes(16)
    db_hash = hashlib.pbkdf2_hmac(HASH_NAME, password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2:{HASH_NAME}:{ITERATIONS}:{salt.hex()}:{db_hash.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password matches the hashed signature."""
    if ph and not hashed_password.startswith("pbkdf2:"):
        try:
            return ph.verify(hashed_password, plain_password)
        except Exception:
            return False
            
    # Fallback PBKDF2 verify
    try:
        parts = hashed_password.split(":")
        if len(parts) != 5 or parts[0] != "pbkdf2":
            return False
        hash_name = parts[1]
        iterations = int(parts[2])
        salt = bytes.fromhex(parts[3])
        stored_hash = bytes.fromhex(parts[4])
        
        calc_hash = hashlib.pbkdf2_hmac(hash_name, plain_password.encode("utf-8"), salt, iterations)
        return secrets.compare_digest(calc_hash, stored_hash)
    except Exception:
        return False

def validate_password_strength(password: str) -> Tuple[bool, list[str]]:
    """Checks password complexity constraints (min 8 chars, 1 uppercase, 1 lowercase, 1 digit)."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one numeric digit.")
        
    return len(errors) == 0, errors
