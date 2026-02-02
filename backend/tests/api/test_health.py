"""Tests for the health check endpoint."""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test that health check endpoint returns 200 OK.

    This test verifies the GET /health endpoint returns a successful response
    with status and database availability indicators.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["database"] is True


def test_root_endpoint(client: TestClient):
    """Test that root endpoint returns welcome message.

    This test verifies the GET / endpoint returns the expected welcome message
    with API version information.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to WebApp API" in data["message"]
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"


def test_api_info_endpoint(client: TestClient):
    """Test that API info endpoint returns operational status.

    This test verifies the GET /api/v1/info endpoint returns correct API metadata.
    """
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "WebApp API"
    assert data["version"] == "0.1.0"
    assert data["status"] == "operational"
