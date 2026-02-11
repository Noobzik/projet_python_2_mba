"""Unit tests for customer routes.

This module tests all customer-related API endpoints.
"""

from fastapi.testclient import TestClient


def test_get_customers(client: TestClient) -> None:
    """Test GET /api/customers endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert "customers" in data
    assert "page" in data
    assert "total" in data
    assert isinstance(data["customers"], list)


def test_get_customers_pagination(client: TestClient) -> None:
    """Test GET /api/customers with pagination.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/customers?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["customers"]) <= 2


def test_get_customer_profile(client: TestClient) -> None:
    """Test GET /api/customers/{customer_id} endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/customers/1556")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1556
    assert "transactions_count" in data
    assert "avg_amount" in data
    assert "fraudulent" in data


def test_get_customer_profile_not_found(client: TestClient) -> None:
    """Test GET /api/customers/{customer_id} with invalid ID.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/customers/99999")
    assert response.status_code == 404


def test_get_top_customers(client: TestClient) -> None:
    """Test GET /api/customers/top endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/customers/top?n=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3
    for customer in data:
        assert "id" in customer
        assert "total_amount" in customer
        assert "transactions_count" in customer

    if len(data) > 1:
        assert data[0]["total_amount"] >= data[1]["total_amount"]
