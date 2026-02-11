"""Unit tests for transaction routes.

This module tests all transaction-related API endpoints.
"""

from fastapi.testclient import TestClient


def test_get_transactions(client: TestClient) -> None:
    """Test GET /api/transactions endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "page" in data
    assert "total" in data
    assert data["page"] == 1


def test_get_transactions_with_filters(client: TestClient) -> None:
    """Test GET /api/transactions with filters.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/transactions?use_chip=Chip")
    assert response.status_code == 200
    data = response.json()
    for tx in data["transactions"]:
        assert "Chip" in tx["use_chip"]


def test_get_transactions_fraud_filter(client: TestClient) -> None:
    """Test GET /api/transactions with fraud filter.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/transactions?isFraud=1")
    assert response.status_code == 200
    data = response.json()
    for tx in data["transactions"]:
        assert tx["isFraud"] == 1


def test_get_transaction_by_id(client: TestClient) -> None:
    """Test GET /api/transactions/{id} endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/transactions/tx_0000000")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "tx_0000000"


def test_get_transaction_by_id_not_found(client: TestClient) -> None:
    """Test GET /api/transactions/{id} with invalid ID.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/transactions/invalid_id")
    assert response.status_code == 404


def test_search_transactions(client: TestClient) -> None:
    """Test POST /api/transactions/search endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    search_criteria = {
        "use_chip": "Swipe",
        "isFraud": 0
    }
    response = client.post("/api/transactions/search", json=search_criteria)
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data


def test_search_transactions_amount_range(client: TestClient) -> None:
    """Test POST /api/transactions/search with amount range.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    search_criteria = {
        "amount_range": [1000, 10000]
    }
    response = client.post("/api/transactions/search", json=search_criteria)
    assert response.status_code == 200
    data = response.json()
    for tx in data["transactions"]:
        assert 1000 <= tx["amount"] <= 10000


def test_get_transaction_types(client: TestClient) -> None:
    """Test GET /api/transactions/types endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/transactions/types")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_recent_transactions(client: TestClient) -> None:
    """Test GET /api/transactions/recent endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/transactions/recent?n=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_delete_transaction(client: TestClient) -> None:
    """Test DELETE /api/transactions/{id} endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.delete("/api/transactions/tx_0000000")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"


def test_delete_transaction_not_found(client: TestClient) -> None:
    """Test DELETE /api/transactions/{id} with invalid ID.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.delete("/api/transactions/invalid_id")
    assert response.status_code == 404


def test_get_transactions_by_customer(client: TestClient) -> None:
    """Test GET /api/transactions/by-customer/{customer_id} endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/transactions/by-customer/1556")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    for tx in data["transactions"]:
        assert tx["client_id"] == 1556


def test_get_transactions_to_customer(client: TestClient) -> None:
    """Test GET /api/transactions/to-customer/{customer_id} endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/transactions/to-customer/1557")
    assert response.status_code == 200
    data = response.json()
    # Returns empty list for Kaggle dataset (no customer-to-customer transfers)
    assert isinstance(data, list)
    assert len(data) == 0
