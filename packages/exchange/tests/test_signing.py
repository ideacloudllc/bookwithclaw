"""Tests for cryptographic signing and JWT utilities."""

import pytest

from app.core.signing import (
    canonical_json,
    create_jwt_token,
    generate_keypair,
    sign_message,
    verify_jwt_token,
    verify_signature,
)


def test_generate_keypair():
    """Test Ed25519 keypair generation."""
    public_key, private_key = generate_keypair()
    
    # Validate format (64-char hex for 32-byte keys)
    assert len(public_key) == 64
    assert len(private_key) == 64
    assert all(c in "0123456789abcdef" for c in public_key)
    assert all(c in "0123456789abcdef" for c in private_key)


def test_sign_and_verify():
    """Test signing and signature verification."""
    public_key, private_key = generate_keypair()
    message = b"test message"
    
    # Sign
    signature = sign_message(message, private_key)
    assert len(signature) == 128  # 64-byte signature in hex
    
    # Verify correct
    assert verify_signature(message, signature, public_key)
    
    # Verify fails on tampered message
    assert not verify_signature(b"different message", signature, public_key)
    
    # Verify fails on tampered signature
    bad_sig = signature[:-2] + "00"
    assert not verify_signature(message, bad_sig, public_key)


def test_canonical_json():
    """Test canonical JSON serialization."""
    obj1 = {"b": 2, "a": 1, "c": {"z": 3, "y": 2}}
    obj2 = {"a": 1, "c": {"y": 2, "z": 3}, "b": 2}
    
    # Same dict, different key order, should serialize identically
    json1 = canonical_json(obj1)
    json2 = canonical_json(obj2)
    
    assert json1 == json2
    assert json1 == b'{"a":1,"b":2,"c":{"y":2,"z":3}}'


def test_create_and_verify_jwt():
    """Test JWT token creation and verification."""
    agent_id = "test-agent-123"
    public_key = "abcd1234" * 8  # 64-char hex
    role = "buyer"
    
    # Create
    token = create_jwt_token(agent_id, public_key, role)
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Verify
    payload = verify_jwt_token(token)
    assert payload is not None
    assert payload["agent_id"] == agent_id
    assert payload["public_key"] == public_key
    assert payload["role"] == role
    assert "iat" in payload
    assert "exp" in payload


def test_invalid_jwt():
    """Test JWT verification with invalid token."""
    assert verify_jwt_token("invalid.token.string") is None
    assert verify_jwt_token("") is None
    assert verify_jwt_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature") is None
