from __future__ import annotations

from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient
from banking_api.main import app
from banking_api.services import dataset_loader

# --- 1. FONCTION D'INJECTION DE DONNÉES (MOCK) ---
def setup_mock_data():
    """
    Injecte un faux dataset complet dans le service.
    """
    df = pd.DataFrame([
        # Transaction 1 : Normale
        {
            "step": 1, "type": "PAYMENT", "amount": 10.0,
            "nameOrig": "C1", "nameDest": "M1",
            "oldbalanceOrg": 100.0, "newbalanceOrig": 90.0,
            "oldbalanceDest": 0.0, "newbalanceDest": 0.0,
            "isFraud": 0, "isFlaggedFraud": 0
        },
        # Transaction 2 : Fraude (Gros montant + Vidage de compte)
        {
            "step": 1, "type": "TRANSFER", "amount": 500000.0,
            "nameOrig": "C2", "nameDest": "C3",
            "oldbalanceOrg": 500000.0, "newbalanceOrig": 0.0,
            "oldbalanceDest": 0.0, "newbalanceDest": 0.0,
            "isFraud": 1, "isFlaggedFraud": 0
        },
        # Transaction 3 : Autre fraude flaggée
        {
            "step": 2, "type": "CASH_OUT", "amount": 30.0,
            "nameOrig": "C2", "nameDest": "C4",
            "oldbalanceOrg": 30.0, "newbalanceOrig": 0.0,
            "oldbalanceDest": 0.0, "newbalanceDest": 0.0,
            "isFraud": 1, "isFlaggedFraud": 1
        },
    ])
    
    # On force les types pour éviter les erreurs
    df['step'] = df['step'].astype('int32')
    df['amount'] = df['amount'].astype('float32')
    df['isFraud'] = df['isFraud'].astype('int8')
    
    # On écrase le cache du loader
    dataset_loader._DATAFRAME_CACHE = df
    return df

# --- 2. LES TESTS ---

def test_fraud_summary():
    """Vérifie le résumé (Total et Fraudes)."""
    setup_mock_data()
    with TestClient(app) as client:
        r = client.get("/api/fraud/summary")
        assert r.status_code == 200
        data = r.json()
        
        assert data["total_transactions"] == 3
        assert data["total_frauds"] == 2
        assert data["flagged_frauds"] == 1

def test_fraud_transactions_list():
    """Vérifie la pagination des fraudes."""
    setup_mock_data()
    with TestClient(app) as client:
        r = client.get("/api/fraud/transactions?page=1&limit=10")
        assert r.status_code == 200
        data = r.json()
        
        # --- CORRECTION ICI ---
        # On récupère 'transactions' (ou 'items' au cas où)
        tx_list = data.get("transactions", data.get("items"))
        
        assert len(tx_list) == 2
        assert tx_list[0]["isFraud"] == 1

def test_fraud_top_customers():
    """Vérifie le top des clients frauduleux."""
    setup_mock_data()
    with TestClient(app) as client:
        r = client.get("/api/fraud/top-customers?n=2")
        assert r.status_code == 200
        data = r.json()
        
        # On récupère 'customers' (ou 'items')
        cust_list = data.get("customers", data.get("items"))
        
        assert cust_list[0]["id"] == "C2"
        assert cust_list[0]["fraud_count"] == 2

def test_fraud_predict():
    """Teste la prédiction de risque (Scoring)."""
    with TestClient(app) as client:
        
        # Cas A : Risque Critique
        payload_risk = {
            "type": "TRANSFER",
            "amount": 250000.0,
            "oldbalanceOrg": 250000.0,
            "newbalanceOrig": 0.0
        }
        r = client.post("/api/fraud/predict", json=payload_risk)
        assert r.status_code == 200
        res = r.json()
        assert res["isFraud"] is True
        assert res["risk_level"] == "CRITICAL"
        
        # Cas B : Risque Faible
        payload_safe = {
            "type": "PAYMENT",
            "amount": 15.0,
            "oldbalanceOrg": 100.0,
            "newbalanceOrig": 85.0
        }
        r = client.post("/api/fraud/predict", json=payload_safe)
        assert r.status_code == 200
        res = r.json()
        assert res["isFraud"] is False