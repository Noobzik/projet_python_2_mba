"""Unit tests for statistics routes.

This module tests all statistics-related API endpoints.
"""

from fastapi.testclient import TestClient


def test_get_stats_overview(client: TestClient) -> None:
    """Test GET /api/stats/overview endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_transactions" in data
    assert "fraud_rate" in data
    assert "avg_amount" in data
    assert "most_common_type" in data
    assert data["total_transactions"] > 0


def test_get_amount_distribution(client: TestClient) -> None:
    """Test GET /api/stats/amount-distribution endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/stats/amount-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "bins" in data
    assert "counts" in data
    assert len(data["bins"]) == len(data["counts"])


def test_get_amount_distribution_custom_bins(client: TestClient) -> None:
    """Test GET /api/stats/amount-distribution with custom bins.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/stats/amount-distribution?bins=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["bins"]) == 5


def test_get_stats_by_type(client: TestClient) -> None:
    """Test GET /api/stats/by-type endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/stats/by-type")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for item in data:
        assert "type" in item
        assert "count" in item
        assert "avg_amount" in item
        assert "fraud_rate" in item


def test_get_daily_stats(client: TestClient) -> None:
    """Test GET /api/stats/daily endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/stats/daily")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for item in data:
        assert "step" in item
        assert "count" in item
        assert "avg_amount" in item
        assert "fraud_count" in item
