from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fraud_summary():
    r = client.get("/api/fraud/summary")
    assert r.status_code == 200
    body = r.json()
    assert "total_frauds" in body
    assert "precision" in body


def test_fraud_by_type():
    r = client.get("/api/fraud/by-type")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_fraud_predict():
    payload = {
        "type": "TRANSFER",
        "amount": 3500.0,
        "oldbalanceOrg": 15000.0,
        "newbalanceOrig": 11500.0,
    }
    r = client.post("/api/fraud/predict", json=payload)
    assert r.status_code == 200
    assert "isFraud" in r.json()
    assert "probability" in r.json()
