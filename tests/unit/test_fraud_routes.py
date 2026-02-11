"""Unit tests for fraud detection routes.

This module tests all fraud-related API endpoints.
"""

from fastapi.testclient import TestClient


def test_get_fraud_summary(client: TestClient) -> None:
    """Test GET /api/fraud/summary endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_frauds" in data
    assert "flagged" in data
    assert "fraud_rate" in data
    assert "total_fraud_amount" in data
    assert isinstance(data["total_frauds"], int)


def test_get_fraud_by_type(client: TestClient) -> None:
    """Test GET /api/fraud/by-type endpoint.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    response = client.get("/api/fraud/by-type")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for item in data:
        assert "type" in item
        assert "fraud_rate" in item
        assert "fraud_count" in item
        assert "total_count" in item


def test_predict_fraud_low_risk(client: TestClient) -> None:
    """Test POST /api/fraud/predict with low-risk transaction.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    transaction = {
        "amount": 100.0,
        "use_chip": "Chip Transaction",
        "merchant_state": "ND",
        "mcc": 5411
    }
    response = client.post("/api/fraud/predict", json=transaction)
    assert response.status_code == 200
    data = response.json()
    assert "isFraud" in data
    assert "probability" in data
    assert isinstance(data["isFraud"], bool)
    assert 0.0 <= data["probability"] <= 1.0


def test_predict_fraud_high_risk(client: TestClient) -> None:
    """Test POST /api/fraud/predict with high-risk transaction.

    Parameters
    ----------
    client : TestClient
        FastAPI test client.
    """
    transaction = {
        "amount": 500000.0,
        "use_chip": "Online Transaction",
        "merchant_state": "CA",
        "mcc": 5999
    }
    response = client.post("/api/fraud/predict", json=transaction)
    assert response.status_code == 200
    data = response.json()
    assert "isFraud" in data
    assert "probability" in data
    assert data["probability"] > 0.5
