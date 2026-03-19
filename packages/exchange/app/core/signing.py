"""Ed25519 cryptographic signing and verification for agents."""

import os
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def generate_keypair() -> Tuple[str, str]:
    """
    Generate an Ed25519 keypair.
    
    Returns:
        Tuple of (private_key_hex, public_key_hex)
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
    
    return private_hex, public_hex


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
