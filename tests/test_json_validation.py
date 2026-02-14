
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import des routes
from app.router.fraude import router_fraude
from app.router.transaction import router as router_transactions
from app.router.customer import router_customers
from app.router.system import router_system
from app.router.stats import router_stat

# Créer l'application FastAPI avec tous les routers

app = FastAPI()
app.include_router(router_fraude)
app.include_router(router_transactions)
app.include_router(router_customers)
app.include_router(router_system)
app.include_router(router_stat)

client = TestClient(app)

# FRAUDE

# /api/fraud/predict
def test_predict_fraud_valid_json():
    payload = {"type": "TRANSFER", "amount": 1000, "oldbalanceOrg": 5000, "newbalanceOrig": 4000}
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 200

def test_predict_fraud_missing_field():
    payload = {"type": "TRANSFER", "amount": 1000, "oldbalanceOrg": 5000}  # missing newbalanceOrig
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 422

def test_predict_fraud_wrong_type():
    payload = {"type": "TRANSFER", "amount": "mille", "oldbalanceOrg": 5000, "newbalanceOrig": 4000}
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 422

# TRANSACTIONS

# /api/transactions/search (POST)
def test_search_transactions_valid_json():
    payload = {"page": 1, "limit": 10, "tx_type": "TRANSFER", "isFraud": False, "min_amount": 10, "max_amount": 1000}
    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200

def test_search_transactions_missing_optional_fields():
    payload = {"page": 1, "limit": 10}  # optional fields missing
    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Correction : le champ renvoyé s'appelle "type" et non "tx_type"
    assert data["filters_applied"]["type"] is None
    assert data["filters_applied"]["isFraud"] is None
    assert data["filters_applied"]["min_amount"] is None
    assert data["filters_applied"]["max_amount"] is None

def test_search_transactions_wrong_type():
    payload = {"page": "first", "limit": "ten"}  # wrong types
    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 422

# /api/transactions/recent
def test_recent_transactions_route_valid():
    response = client.get("/api/transactions/recent?n=10")
    assert response.status_code == 200

def test_recent_transactions_route_invalid_type():
    response = client.get("/api/transactions/recent?n=abc")  # should be int
    assert response.status_code == 422

def test_recent_transactions_route_negative_value():
    response = client.get("/api/transactions/recent?n=-5")
    assert response.status_code == 200  # logique route accepte n <=0 mais renvoie 0 transactions

# /api/transactions/by-customer/{customer_id} & /to-customer/{customer_id} sont GET → pas de JSON à valider

# CUSTOMERS

# /api/customers/top (GET avec query param)
def test_get_top_customers_query_valid():
    response = client.get("/api/customers/top?n=5")
    assert response.status_code == 200

def test_get_top_customers_query_invalid_type():
    response = client.get("/api/customers/top?n=abc")  # n should be int
    assert response.status_code == 422

# /api/customers (GET) pas de JSON à valider

# SYSTEM

# /api/system/health & /api/system/metadata sont GET sans JSON → juste vérifier 200
def test_system_health_route():
    response = client.get("/api/system/health")
    assert response.status_code == 200

def test_system_metadata_route():
    response = client.get("/api/system/metadata")
    assert response.status_code == 200

# STATS

# /api/stats/daily (GET) pas de JSON → 200
def test_stats_daily_route():
    response = client.get("/api/stats/daily")
    assert response.status_code == 200

# /api/stats/by-type (GET)
def test_stats_by_type_route():
    response = client.get("/api/stats/by-type")
    assert response.status_code == 200

# /api/stats/amount-distribution (GET)
def test_amount_distribution_route():
    response = client.get("/api/stats/amount-distribution")
    assert response.status_code == 200
