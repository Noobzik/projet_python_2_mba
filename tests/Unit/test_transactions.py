from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_transactions():
    response = client.get("/api/transactions")
    assert response.status_code == 200
    assert "transactions" in response.json()

def test_transaction_detail():
    tx = client.get("/api/transactions").json()["transactions"][0]
    response = client.get(f"/api/transactions/{tx['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == tx["id"]

def test_search_transactions():
    payload = {"type": "TRANSFER"}
    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200
