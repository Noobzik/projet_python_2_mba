import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from app.router.transaction import router 

import pandas as pd
import app.services.transaction as transaction_module

#test app.router.transaction

app = FastAPI()
app.include_router(router)

client = TestClient(app)

# GET /api/transactions

@patch("app.router.transaction.get_transactions")
def test_transaction_route(mock_get_transactions):
    mock_get_transactions.return_value = [{"id": "TX1"}, {"id": "TX2"}]

    response = client.get("/api/transactions?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["filters_applied"]["page"] == 1
    assert len(data["data"]) == 2

# GET /api/transactions/types

@patch("app.router.transaction.get_transaction_types")
def test_transaction_types_route(mock_types):
    mock_types.return_value = ["TRANSFER", "DEPOSIT"]
    
    response = client.get("/api/transactions/types")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_types"] == 2
    assert "TRANSFER" in data["types"]

# GET /api/transactions/recent

@patch("app.router.transaction.get_recent_transactions")
def test_recent_transactions_route(mock_recent):
    mock_recent.return_value = [{"id": "TX100"}, {"id": "TX101"}]

    response = client.get("/api/transactions/recent?n=2")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total"] == 2

def test_recent_transactions_route_zero():
    response = client.get("/api/transactions/recent?n=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["transactions"] == []

# GET /api/transactions/{id}

@patch("app.router.transaction.get_transaction_by_id")
def test_get_transaction_by_id_route_found(mock_get):
    mock_get.return_value = {"id": "TX123", "amount": 100}
    response = client.get("/api/transactions/TX123")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["transaction"]["id"] == "TX123"

@patch("app.router.transaction.get_transaction_by_id")
def test_get_transaction_by_id_route_not_found(mock_get):
    mock_get.return_value = None
    response = client.get("/api/transactions/UNKNOWN")
    assert response.status_code == 404
    assert "introuvable" in response.json()["detail"]

# POST /api/transactions/search

@patch("app.router.transaction.search_transactions")
def test_search_transactions_route(mock_search):
    mock_search.return_value = [{"id": "TX1"}]
    payload = {
        "page": 1,
        "limit": 5,
        "tx_type": "TRANSFER",
        "isFraud": False,
        "min_amount": 10,
        "max_amount": 1000
    }
    response = client

#test app.services.transactions

# Fixture : DataFrame simulé

@pytest.fixture(autouse=True)
def setup_sample_df(monkeypatch):
    data = {
        "Transaction ID": ["T1", "T2", "TEST_3", "T4", "TEST_5"],
        "Sender Account ID": ["ACC1", "ACC2", "ACC1", "ACC3", "ACC2"],
        "Receiver Account ID": ["ACC4", "ACC5", "ACC6", "ACC1", "ACC3"],
        "Transaction Amount": [100, 200, 300, 400, 500],
        "Transaction Type": ["Deposit", "Withdrawal", "Deposit", "Transfer", "Transfer"],
        "Fraud Flag": [0, 1, 0, 0, 1],
        "Is Test": [False, False, True, False, True],
        "Timestamp": pd.date_range("2026-01-01", periods=5)
    }
    df = pd.DataFrame(data)
    monkeypatch.setattr(transaction_module, "df", df)

# 1. get_transactions

def test_get_transactions_basic():
    result = transaction_module.get_transactions()
    assert result["page"] == 1
    assert result["limit"] == 5
    assert result["total"] == 5
    assert len(result["results"]) == 5

def test_get_transactions_filter_type():
    result = transaction_module.get_transactions(type="Deposit")
    assert all(r["Transaction Type"] == "Deposit" for r in result["results"])
    assert result["total"] == 2

def test_get_transactions_filter_fraud():
    result = transaction_module.get_transactions(isFraud=1)
    assert all(r["Fraud Flag"] == 1 for r in result["results"])
    assert result["total"] == 2

def test_get_transactions_amount_range():
    result = transaction_module.get_transactions(min_amount=200, max_amount=400)
    for r in result["results"]:
        assert 200 <= r["Transaction Amount"] <= 400

def test_get_transactions_page_limit_exceeds_total():
    result = transaction_module.get_transactions(page=2, limit=10)
    assert result["results"] == []  # pas de résultats sur la 2e page

# 2. get_transaction_by_id

def test_get_transaction_by_id_found():
    result = transaction_module.get_transaction_by_id("T1")
    assert result["Transaction ID"] == "T1"

def test_get_transaction_by_id_not_found():
    result = transaction_module.get_transaction_by_id("T999")
    assert result is None

def test_get_transaction_by_id_empty_id():
    result = transaction_module.get_transaction_by_id("")
    assert result is None

# 3. search_transactions

def test_search_transactions_basic():
    payload = {"page": 1, "limit": 2}
    result = transaction_module.search_transactions(payload)
    assert result["page"] == 1
    assert result["limit"] == 2
    assert len(result["results"]) <= 2

def test_search_transactions_filter_type_and_fraud():
    payload = {"type": "Transfer", "isFraud": 1}
    result = transaction_module.search_transactions(payload)
    assert all(r["Transaction Type"] == "Transfer" and r["Fraud Flag"] == 1 for r in result["results"])

def test_search_transactions_amount_range():
    payload = {"amount_range": [200, 400]}
    result = transaction_module.search_transactions(payload)
    for r in result["results"]:
        assert 200 <= r["Transaction Amount"] <= 400

def test_search_transactions_invalid_page_limit():
    payload = {"page": -2, "limit": 0}
    result = transaction_module.search_transactions(payload)
    assert result["page"] == 1
    assert result["limit"] == 10

# 4. get_transaction_types

def test_get_transaction_types_returns_unique_sorted():
    types = transaction_module.get_transaction_types()
    assert types == sorted(list(set(["Deposit", "Withdrawal", "Transfer"])))

# 5. get_recent_transactions

def test_get_recent_transactions_default_n():
    result = transaction_module.get_recent_transactions()
    assert len(result) == 5
    timestamps = [r["Timestamp"] for r in result]
    assert timestamps == sorted(timestamps, reverse=True)

def test_get_recent_transactions_custom_n():
    result = transaction_module.get_recent_transactions(n=2)
    assert len(result) == 2

def test_get_recent_transactions_negative_n():
    result = transaction_module.get_recent_transactions(n=-5)
    assert result == []

# 6. delete_test_transaction

def test_delete_test_transaction_real_forbidden(monkeypatch):
    temp_df = transaction_module.df.copy()
    monkeypatch.setattr(transaction_module, "df", temp_df)
    monkeypatch.setattr(temp_df, "to_excel", lambda *a, **kw: None)

    result = transaction_module.delete_test_transaction("T1")
    assert result["success"] is False
    assert "interdite" in result["message"]

def test_delete_test_transaction_not_found(monkeypatch):
    temp_df = transaction_module.df.copy()
    monkeypatch.setattr(transaction_module, "df", temp_df)
    monkeypatch.setattr(temp_df, "to_excel", lambda *a, **kw: None)

    result = transaction_module.delete_test_transaction("T999")
    assert result["success"] is False
    assert "introuvable" in result["message"]

# 7. get_transactions_by_sender

def test_get_transactions_by_sender():
    result = transaction_module.get_transactions_by_sender("ACC1")
    assert result["sender_account_id"] == "ACC1"
    for r in result["results"]:
        assert r["Sender Account ID"] == "ACC1"

# 8. get_received_transactions

def test_get_received_transactions():
    result = transaction_module.get_received_transactions("ACC3")
    assert result["receiver_account_id"] == "ACC3"
    for r in result["results"]:
        assert r["Receiver Account ID"] == "ACC3"



