"""Unit tests for system routes.

This module tests all system-related API endpoints.
"""

from fastapi.testclient import TestClient


def test_get_health(client: TestClient) -> None:
    """Test GET /api/system/health endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "uptime" in data
    assert "dataset_loaded" in data
    assert "dataset_size" in data
    assert data["status"] in ["ok", "degraded", "error"]


def test_get_metadata(client: TestClient) -> None:
    """Test GET /api/system/metadata endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/system/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "last_update" in data
    assert "dataset_source" in data
    assert "endpoints_count" in data
    assert data["version"] == "1.0.0"
    assert data["endpoints_count"] == 20
