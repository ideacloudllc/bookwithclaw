"""Ed25519 cryptographic signing and verification for agents."""

import json
import os
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from jose import jwt
from app.config import settings


def generate_keypair() -> Tuple[str, str]:
    """
    Generate an Ed25519 keypair.
    
    Returns:
        Tuple of (public_key_hex, private_key_hex)
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Export as hex strings
    private_hex = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    ).hex()
    
    public_hex = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()
    
    return public_hex, private_hex


def sign_message(message: bytes, private_key_hex: str) -> str:
    """
    Sign a message using an Ed25519 private key.
    
    Args:
        message: The message bytes to sign
        private_key_hex: Private key as hex string
        
    Returns:
        Signature as hex string
    """
    private_bytes = bytes.fromhex(private_key_hex)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
    signature = private_key.sign(message)
    return signature.hex()


def verify_signature(message: bytes, signature_hex: str, public_key_hex: str) -> bool:
    """
    Verify an Ed25519 signature.
    
    Args:
        message: The message bytes that were signed
        signature_hex: The signature as hex string
        public_key_hex: The public key as hex string
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        public_bytes = bytes.fromhex(public_key_hex)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
        signature_bytes = bytes.fromhex(signature_hex)
        public_key.verify(signature_bytes, message)
        return True
    except Exception:
        return False


def export_public_key(private_key_hex: str) -> str:
    """
    Export public key from private key.
    
    Args:
        private_key_hex: Private key as hex string
        
    Returns:
        Public key as hex string
    """
    private_bytes = bytes.fromhex(private_key_hex)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return public_bytes.hex()


def canonical_json(obj: Any) -> bytes:
    """
    Serialize object to canonical JSON (deterministic key ordering, no whitespace).
    
    Args:
        obj: Python object to serialize
        
    Returns:
        Canonical JSON as bytes
    """
    return json.dumps(obj, separators=(',', ':'), sort_keys=True).encode()


def create_jwt_token(agent_id: str, public_key: str, role: str = "agent") -> str:
    """
    Create a JWT token for an agent.
    
    Args:
        agent_id: Agent's unique ID
        public_key: Agent's public key (hex string)
        role: Agent role (buyer/seller/agent)
        
    Returns:
        JWT token as string
    """
    now = datetime.utcnow()
    payload = {
        "agent_id": agent_id,
        "public_key": public_key,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=24),
    }
    
    token = jwt.encode(
        payload,
        settings.exchange_secret_key,
        algorithm="HS256"
    )
    
    return token


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token as string
        
    Returns:
        Payload dict if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.exchange_secret_key,
            algorithms=["HS256"]
        )
        return payload
    except Exception:
        return None
