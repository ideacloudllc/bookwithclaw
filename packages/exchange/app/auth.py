"""Authentication utilities for seller registration and login."""

import binascii
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from app.config import settings


def hash_password(password: str) -> str:
    """Hash password with salt using SHA-256."""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${binascii.hexlify(hash_obj).decode('utf-8')}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    try:
        salt, stored_hash = hashed.split('$')
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return binascii.hexlify(hash_obj).decode('utf-8') == stored_hash
    except (ValueError, AttributeError):
        return False


def create_seller_token(seller_id: str, email: str) -> str:
    """Create JWT token for authenticated seller."""
    payload = {
        "seller_id": seller_id,
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(
        payload,
        settings.exchange_secret_key,
        algorithm="HS256"
    )


def verify_seller_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload."""
    try:
        return jwt.decode(
            token,
            settings.exchange_secret_key,
            algorithms=["HS256"]
        )
    except Exception:
        return None
