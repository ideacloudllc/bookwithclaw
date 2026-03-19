"""Tests for health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]
    
    # In test environment, services may not be fully connected
    # but the endpoint should still return valid JSON
    assert data["status"] in ["healthy", "degraded"]
