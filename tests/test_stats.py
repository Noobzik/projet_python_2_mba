import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Body
from unittest.mock import patch
from app.router.stats import router_stat  

# Créer une instance FastAPI pour inclure la route
app = FastAPI()
app.include_router(router_stat)

client = TestClient(app)

# Tests des endpoints statistiques

@patch("app.router.stats.stats_by_type")
def test_get_stats_by_type(mock_stats):
    mock_stats.return_value = {"Deposit": 10, "Withdrawal": 5}
    response = client.get("/api/stats/by-type")
    assert response.status_code == 200
    data = response.json()
    assert data["Deposit"] == 10
    assert data["Withdrawal"] == 5

@patch("app.router.stats.amount_distribution")
def test_get_amount_distribution(mock_dist):
    mock_dist.return_value = {"0-100": 50, "100-500": 30}
    response = client.get("/api/stats/amount-distribution")
    assert response.status_code == 200
    data = response.json()
    assert data["0-100"] == 50
    assert data["100-500"] == 30

@patch("app.router.stats.obtenir_stats_journalieres_completes")
def test_get_stats_daily_history(mock_daily):
    mock_daily.return_value = [
        {"date": "2026-02-13", "Deposit": 5, "Withdrawal": 2},
        {"date": "2026-02-12", "Deposit": 8, "Withdrawal": 1}
    ]
    response = client.get("/api/stats/daily")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["Deposit"] == 5

# Tests des endpoints de fraude

@patch("app.router.stats.calculer_resume_fraude")
def test_get_fraud_summary_success(mock_resume):
    mock_resume.return_value = {"total_fraudes": 3, "taux_fraude": 0.05}
    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_fraudes"] == 3
    assert data["taux_fraude"] == 0.05

@patch("app.router.stats.calculer_resume_fraude")
def test_get_fraud_summary_error(mock_resume):
    mock_resume.return_value = {"error": "Pas de données"}
    response = client.get("/api/fraud/summary")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pas de données"

@patch("app.router.stats.calculer_taux_fraude_par_type")
def test_get_fraud_by_type_success(mock_by_type):
    mock_by_type.return_value = {"Deposit": 0.01, "Withdrawal": 0.03}
    response = client.get("/api/fraud/by-type")
    assert response.status_code == 200
    data = response.json()
    assert data["Deposit"] == 0.01
    assert data["Withdrawal"] == 0.03

@patch("app.router.stats.calculer_taux_fraude_par_type")
def test_get_fraud_by_type_error(mock_by_type):
    mock_by_type.return_value = {"error": "Pas de données"}
    response = client.get("/api/fraud/by-type")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pas de données"

@patch("app.router.stats.simuler_prediction_fraude")
def test_predict_fraud_success(mock_predict):
    mock_predict.return_value = {"is_fraud": True, "score": 0.95}
    payload = {
        "type": "TRANSFER",
        "amount": 1000,
        "oldbalanceOrg": 5000,
        "newbalanceOrig": 4000
    }
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_fraud"] is True
    assert data["score"] == 0.95
