from __future__ import annotations
import pandas as pd
from fastapi.testclient import TestClient
from banking_api.main import app
from banking_api.services import dataset_loader

# --- 1. SETUP DES DONNÉES (MOCK) ---
def setup_mock_data():
    """
    On injecte 3 transactions variées pour tester les filtres de recherche.
    """
    df = pd.DataFrame([
        # Transaction 1 : Petit montant, C1, TRANSFER
        {
            "step": 1, "type": "TRANSFER", "amount": 50.0, 
            "nameOrig": "C1", "nameDest": "C2", 
            "isFraud": 0, "isFlaggedFraud": 0,
            "oldbalanceOrg": 0, "newbalanceOrig": 0, "oldbalanceDest": 0, "newbalanceDest": 0
        },
        # Transaction 2 : Moyen montant (Cible pour la recherche 100-600), C3, TRANSFER
        {
            "step": 1, "type": "TRANSFER", "amount": 500.0, 
            "nameOrig": "C3", "nameDest": "C4", 
            "isFraud": 0, "isFlaggedFraud": 0,
            "oldbalanceOrg": 0, "newbalanceOrig": 0, "oldbalanceDest": 0, "newbalanceDest": 0
        },
        # Transaction 3 : Gros montant, C2, CASH_OUT
        {
            "step": 1, "type": "CASH_OUT", "amount": 700.0, 
            "nameOrig": "C2", "nameDest": "C5", 
            "isFraud": 1, "isFlaggedFraud": 0,
            "oldbalanceOrg": 0, "newbalanceOrig": 0, "oldbalanceDest": 0, "newbalanceDest": 0
        },
    ])
    
    # Force les types
    df['step'] = df['step'].astype('int32')
    df['amount'] = df['amount'].astype('float32')
    df['isFraud'] = df['isFraud'].astype('int8')
    
    # Injection dans le cache
    dataset_loader._DATAFRAME_CACHE = df
    return df

# --- 2. LES TESTS ---

def test_search_by_amount_range():
    """Recherche par montant (entre 100 et 600)."""
    setup_mock_data()
    with TestClient(app) as client:
        # On cherche entre 100 et 600 -> Doit trouver celle de 500.0
        r = client.post("/api/transactions/search", json={"min_amount": 100, "max_amount": 600})
        assert r.status_code == 200
        data = r.json()
        
        # Gestion robuste (liste directe ou pagination)
        if isinstance(data, dict):
            results = data.get("items", data.get("transactions"))
        else:
            results = data

        assert len(results) == 1
        assert results[0]["amount"] == 500.0

def test_search_by_type_and_nameOrig():
    """Recherche combinée : Type + Nom."""
    setup_mock_data()
    with TestClient(app) as client:
        # On cherche TRANSFER fait par C1
        r = client.post("/api/transactions/search", json={"type": "TRANSFER", "nameOrig": "C1"})
        assert r.status_code == 200
        data = r.json()
        
        if isinstance(data, dict):
            results = data.get("items", data.get("transactions"))
        else:
            results = data

        assert len(results) == 1
        assert results[0]["type"] == "TRANSFER"
        assert results[0]["nameOrig"] == "C1"

def test_search_invalid_range_returns_400():
    """Vérifie la validation (Min > Max interdit)."""
    setup_mock_data()
    with TestClient(app) as client:
        # Min (10) > Max (1) -> Erreur
        r = client.post("/api/transactions/search", json={"min_amount": 10, "max_amount": 1})
        assert r.status_code == 400