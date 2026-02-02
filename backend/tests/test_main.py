from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]
    assert response.json()["version"] == "0.1.0"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_info():
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"
