"""Tests for agent registration endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.core.signing import generate_keypair


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app
    return TestClient(app)


def test_register_agent_success(client: TestClient):
    """Test successful agent registration."""
    public_key, _ = generate_keypair()
    
    response = client.post(
        "/agents/register",
        json={
            "public_key": public_key,
            "role": "buyer",
            "email": "buyer@example.com",
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert "auth_token" in data
    assert data["expires_in"] == 86400


def test_register_agent_seller(client: TestClient):
    """Test registration as seller."""
    public_key, _ = generate_keypair()
    
    response = client.post(
        "/agents/register",
        json={
            "public_key": public_key,
            "role": "seller",
            "email": "seller@example.com",
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert "auth_token" in data


def test_register_agent_invalid_role(client: TestClient):
    """Test registration with invalid role."""
    public_key, _ = generate_keypair()
    
    response = client.post(
        "/agents/register",
        json={
            "public_key": public_key,
            "role": "admin",  # Invalid role
            "email": "test@example.com",
        }
    )
    
    assert response.status_code == 400
    assert "role" in response.json()["detail"].lower()


def test_register_agent_invalid_public_key(client: TestClient):
    """Test registration with invalid public key format."""
    response = client.post(
        "/agents/register",
        json={
            "public_key": "invalid_key",  # Not 64-char hex
            "role": "buyer",
            "email": "test@example.com",
        }
    )
    
    assert response.status_code == 400
    assert "public_key" in response.json()["detail"].lower()


def test_register_agent_duplicate_public_key(client: TestClient):
    """Test registration with duplicate public key."""
    public_key, _ = generate_keypair()
    
    # First registration
    response1 = client.post(
        "/agents/register",
        json={
            "public_key": public_key,
            "role": "buyer",
            "email": "first@example.com",
        }
    )
    assert response1.status_code == 200
    
    # Duplicate public key
    response2 = client.post(
        "/agents/register",
        json={
            "public_key": public_key,
            "role": "seller",
            "email": "second@example.com",
        }
    )
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()


def test_register_agent_duplicate_email(client: TestClient):
    """Test registration with duplicate email."""
    public_key1, _ = generate_keypair()
    public_key2, _ = generate_keypair()
    
    # First registration
    response1 = client.post(
        "/agents/register",
        json={
            "public_key": public_key1,
            "role": "buyer",
            "email": "shared@example.com",
        }
    )
    assert response1.status_code == 200
    
    # Duplicate email
    response2 = client.post(
        "/agents/register",
        json={
            "public_key": public_key2,
            "role": "seller",
            "email": "shared@example.com",
        }
    )
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()


def test_register_agent_invalid_email(client: TestClient):
    """Test registration with invalid email."""
    public_key, _ = generate_keypair()
    
    response = client.post(
        "/agents/register",
        json={
            "public_key": public_key,
            "role": "buyer",
            "email": "not-an-email",
        }
    )
    
    assert response.status_code == 422  # Validation error
