# tests/test_fraud_routes.py

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch

# Importer la route
from app.router.fraude import router_fraude

# Créer une instance FastAPI pour tester la route
app = FastAPI()
app.include_router(router_fraude)

client = TestClient(app)

# Test GET /api/fraud/summary

@patch("app.router.fraude.calculer_resume_fraude")
def test_get_fraud_summary_success(mock_resume):
    # Simuler le retour de la fonction de service
    mock_resume.return_value = {"total_fraudes": 5, "taux_fraude": 0.02}
    
    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_fraudes"] == 5
    assert data["taux_fraude"] == 0.02

@patch("app.router.fraude.calculer_resume_fraude")
def test_get_fraud_summary_error(mock_resume):
    # Simuler un retour avec "error"
    mock_resume.return_value = {"error": "Pas de données"}
    
    response = client.get("/api/fraud/summary")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pas de données"

# Test GET /api/fraud/by-type

@patch("app.router.fraude.calculer_taux_fraude_par_type")
def test_get_fraud_by_type_success(mock_by_type):
    mock_by_type.return_value = {"Deposit": 0.01, "Withdrawal": 0.03}
    
    response = client.get("/api/fraud/by-type")
    assert response.status_code == 200
    data = response.json()
    assert data["Deposit"] == 0.01
    assert data["Withdrawal"] == 0.03

@patch("app.router.fraude.calculer_taux_fraude_par_type")
def test_get_fraud_by_type_error(mock_by_type):
    mock_by_type.return_value = {"error": "Pas de données"}
    
    response = client.get("/api/fraud/by-type")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pas de données"

# Test POST /api/fraud/predict

@patch("app.router.fraude.simuler_prediction_fraude")
def test_predict_fraud_success(mock_predict):
    # Simuler une prédiction
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
