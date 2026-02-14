from __future__ import annotations
import pandas as pd
from fastapi.testclient import TestClient
from banking_api.main import app
from banking_api.services import dataset_loader

# --- 1. SETUP DES DONNÉES (MOCK) ---
def setup_mock_data():
    """
    On crée un scénario avec des échanges entre C1, C2 et C3.
    """
    df = pd.DataFrame([
        # Transaction 1 : C1 envoie de l'argent (nameOrig = C1)
        {
            "step": 1, "type": "TRANSFER", "amount": 10.0, 
            "nameOrig": "C1", "nameDest": "C2", 
            "isFraud": 0, "isFlaggedFraud": 0,
            "oldbalanceOrg": 100, "newbalanceOrig": 90, "oldbalanceDest": 0, "newbalanceDest": 10
        },
        # Transaction 2 : C1 retire de l'argent (nameOrig = C1)
        {
            "step": 1, "type": "CASH_OUT", "amount": 20.0, 
            "nameOrig": "C1", "nameDest": "C3", 
            "isFraud": 0, "isFlaggedFraud": 0,
            "oldbalanceOrg": 90, "newbalanceOrig": 70, "oldbalanceDest": 0, "newbalanceDest": 20
        },
        # Transaction 3 : C1 reçoit de l'argent (nameDest = C1)
        {
            "step": 2, "type": "TRANSFER", "amount": 30.0, 
            "nameOrig": "C2", "nameDest": "C1", 
            "isFraud": 0, "isFlaggedFraud": 0,
            "oldbalanceOrg": 100, "newbalanceOrig": 70, "oldbalanceDest": 70, "newbalanceDest": 100
        },
    ])
    
    # Typage strict pour éviter les bugs
    df['step'] = df['step'].astype('int32')
    df['amount'] = df['amount'].astype('float32')
    df['isFraud'] = df['isFraud'].astype('int8')
    
    # Injection dans le cache
    dataset_loader._DATAFRAME_CACHE = df
    return df

# --- 2. LES TESTS ---

def test_by_customer_returns_matching_nameOrig():
    """Vérifie les transactions émises par C1."""
    setup_mock_data()
    with TestClient(app) as client:
        # On demande toutes les transactions faites PAR C1
        r = client.get("/api/transactions/by-customer/C1")
        assert r.status_code == 200
        data = r.json()
        
        # Gestion flexible : soit une liste directe, soit paginée {"items": [...]}
        if isinstance(data, dict):
            tx_list = data.get("items", data.get("transactions", []))
        else:
            tx_list = data
            
        # C1 a fait 2 transactions (Envoyé 10 et Retiré 20)
        assert len(tx_list) == 2
        assert all(tx["nameOrig"] == "C1" for tx in tx_list)

def test_to_customer_returns_matching_nameDest():
    """Vérifie les transactions reçues par C1."""
    setup_mock_data()
    with TestClient(app) as client:
        # On demande toutes les transactions reçues PAR C1
        r = client.get("/api/transactions/to-customer/C1")
        assert r.status_code == 200
        data = r.json()
        
        # Gestion flexible
        if isinstance(data, dict):
            tx_list = data.get("items", data.get("transactions", []))
        else:
            tx_list = data

        # C1 a reçu 1 seule transaction (de C2)
        assert len(tx_list) == 1
        assert tx_list[0]["nameDest"] == "C1"