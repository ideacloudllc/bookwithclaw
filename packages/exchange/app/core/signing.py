"""Ed25519 cryptographic signing and JWT utilities."""

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from jose import JWTError, jwt

from app.config import settings


def generate_keypair() -> tuple[str, str]:
    """
    Generate an Ed25519 keypair.
    
    Returns:
        (public_key_hex, private_key_hex)
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    private_hex = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    ).hex()
    
    public_key = private_key.public_key()
    public_hex = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()
    
    return public_hex, private_hex


def verify_signature(
    message: bytes,
    signature_hex: str,
    public_key_hex: str,
) -> bool:
    """
    Verify an Ed25519 signature.
    
    Args:
        message: The original message bytes
        signature_hex: Hex-encoded signature
        public_key_hex: Hex-encoded public key
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        signature = bytes.fromhex(signature_hex)
        public_key_bytes = bytes.fromhex(public_key_hex)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
        public_key.verify(signature, message)
        return True
    except Exception:
        return False


def sign_message(message: bytes, private_key_hex: str) -> str:
    """
    Sign a message with an Ed25519 private key.
    
    Args:
        message: The message bytes to sign
        private_key_hex: Hex-encoded private key
        
    Returns:
        Hex-encoded signature
    """
    private_key_bytes = bytes.fromhex(private_key_hex)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    signature = private_key.sign(message)
    return signature.hex()


def create_jwt_token(agent_id: str, public_key: str, role: str) -> str:
    """
    Create a JWT token for an agent.
    
    Args:
        agent_id: Unique agent identifier
        public_key: Agent's public key (hex)
        role: "buyer" or "seller"
        
    Returns:
        JWT token string
    """
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=24)
    
    payload = {
        "agent_id": agent_id,
        "public_key": public_key,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    
    token = jwt.encode(
        payload,
        settings.exchange_secret_key,
        algorithm="HS256",
    )
    return token


def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dict if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.exchange_secret_key,
            algorithms=["HS256"],
        )
        return payload
    except JWTError:
        return None


def canonical_json(obj: dict) -> bytes:
    """
    Serialize a dict to canonical JSON (no spaces, sorted keys).
    
    Args:
        obj: Dictionary to serialize
        
    Returns:
        UTF-8 encoded JSON bytes
    """
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
