"""
API tests for all routes.

This module tests all 20 API endpoints with HTTP requests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app


client = TestClient(app)


@pytest.fixture
def mock_transactions():
    """Mock transaction data."""
    return [
        {
            "id": "tx_0000001",
            "step": 1,
            "type": "PAYMENT",
            "amount": 100.0,
            "nameOrig": "C001",
            "oldbalanceOrg": 1000.0,
            "newbalanceOrig": 900.0,
            "nameDest": "M001",
            "oldbalanceDest": 0.0,
            "newbalanceDest": 0.0,
            "isFraud": 0,
            "isFlaggedFraud": 0,
        },
        {
            "id": "tx_0000002",
            "step": 1,
            "type": "TRANSFER",
            "amount": 5000.0,
            "nameOrig": "C002",
            "oldbalanceOrg": 10000.0,
            "newbalanceOrig": 5000.0,
            "nameDest": "C003",
            "oldbalanceDest": 0.0,
            "newbalanceDest": 5000.0,
            "isFraud": 1,
            "isFlaggedFraud": 0,
        },
    ]


@pytest.fixture(autouse=True)
def setup_mock_data(mock_transactions):
    """Setup mock data for all tests."""
    from app.services import transactions_service, stats_service, fraud_detection_service, customer_service
    
    with patch.object(transactions_service, '_get_data', return_value=mock_transactions), \
         patch.object(stats_service, '_get_data', return_value=mock_transactions), \
         patch.object(fraud_detection_service, '_get_data', return_value=mock_transactions), \
         patch.object(customer_service, '_get_data', return_value=mock_transactions):
        yield


# TRANSACTIONS ROUTES (8)
def test_list_transactions():
    """Test GET /api/transactions."""
    response = client.get("/api/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "page" in data


def test_get_transaction_by_id():
    """Test GET /api/transactions/{id}."""
    response = client.get("/api/transactions/tx_0000001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "tx_0000001"


def test_get_transaction_not_found():
    """Test GET with invalid ID."""
    response = client.get("/api/transactions/tx_9999999")
    assert response.status_code == 404


def test_search_transactions():
    """Test POST /api/transactions/search."""
    response = client.post(
        "/api/transactions/search",
        json={"type": "TRANSFER", "isFraud": 1}
    )
    assert response.status_code == 200


def test_get_transaction_types():
    """Test GET /api/transactions/types."""
    response = client.get("/api/transactions/types")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_recent_transactions():
    """Test GET /api/transactions/recent."""
    response = client.get("/api/transactions/recent?n=2")
    assert response.status_code == 200


def test_delete_transaction():
    """Test DELETE /api/transactions/{id}."""
    response = client.delete("/api/transactions/tx_0000001")
    assert response.status_code == 200


def test_get_transactions_by_customer():
    """Test GET /api/transactions/by-customer/{customer_id}."""
    response = client.get("/api/transactions/by-customer/C001")
    assert response.status_code == 200


def test_get_transactions_to_customer():
    """Test GET /api/transactions/to-customer/{customer_id}."""
    response = client.get("/api/transactions/to-customer/M001")
    assert response.status_code == 200


# STATS ROUTES (4)
def test_get_stats_overview():
    """Test GET /api/stats/overview."""
    response = client.get("/api/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_transactions" in data


def test_get_amount_distribution():
    """Test GET /api/stats/amount-distribution."""
    response = client.get("/api/stats/amount-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "bins" in data


def test_get_stats_by_type():
    """Test GET /api/stats/by-type."""
    response = client.get("/api/stats/by-type")
    assert response.status_code == 200


def test_get_daily_stats():
    """Test GET /api/stats/daily."""
    response = client.get("/api/stats/daily")
    assert response.status_code == 200


# FRAUD ROUTES (3)
def test_get_fraud_summary():
    """Test GET /api/fraud/summary."""
    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_frauds" in data


def test_get_fraud_by_type():
    """Test GET /api/fraud/by-type."""
    response = client.get("/api/fraud/by-type")
    assert response.status_code == 200


def test_predict_fraud():
    """Test POST /api/fraud/predict."""
    response = client.post(
        "/api/fraud/predict",
        json={
            "type": "TRANSFER",
            "amount": 5000.0,
            "oldbalanceOrg": 10000.0,
            "newbalanceOrig": 5000.0,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "isFraud" in data
    assert "probability" in data


# CUSTOMERS ROUTES (3)
def test_list_customers():
    """Test GET /api/customers."""
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert "customers" in data


def test_get_customer_profile():
    """Test GET /api/customers/{customer_id}."""
    response = client.get("/api/customers/C001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "C001"


def test_get_top_customers():
    """Test GET /api/customers/top."""
    response = client.get("/api/customers/top?n=2")
    assert response.status_code == 200


# SYSTEM ROUTES (2)
def test_get_health():
    """Test GET /api/system/health."""
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_get_metadata():
    """Test GET /api/system/metadata."""
    response = client.get("/api/system/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data


def test_root_endpoint():
    """Test GET / root endpoint."""
    response = client.get("/")
    assert response.status_code == 200