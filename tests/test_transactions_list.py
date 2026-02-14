from __future__ import annotations
import pandas as pd
from fastapi.testclient import TestClient
from banking_api.main import app
from banking_api.services import dataset_loader
from banking_api.services.transactions_service import reset_deleted_ids

# --- 1. SETUP DES DONNÉES (MOCK) ---
def setup_mock_data():
    """
    On injecte 2 transactions (1 TRANSFER, 1 CASH_OUT) pour tester la liste et le filtrage.
    """
    df = pd.DataFrame([
        # Transaction 1 : TRANSFER
        {
            "step": 1, "type": "TRANSFER", "amount": 100.0, 
            "nameOrig": "C1", "nameDest": "C2", 
            "isFraud": 0, "isFlaggedFraud": 0,
            "oldbalanceOrg": 0, "newbalanceOrig": 0, "oldbalanceDest": 0, "newbalanceDest": 0
        },
        # Transaction 2 : CASH_OUT (Fraude)
        {
            "step": 1, "type": "CASH_OUT", "amount": 500.0, 
            "nameOrig": "C2", "nameDest": "C3", 
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

def test_get_transactions_list_returns_data():
    """Vérifie que l'API retourne bien la liste paginée."""
    setup_mock_data()
    reset_deleted_ids() # On s'assure qu'aucune suppression précédente ne gêne

    with TestClient(app) as client:
        r = client.get("/api/transactions?page=1&limit=10")
        assert r.status_code == 200
        data = r.json()

        # Vérification de la pagination
        assert data["page"] == 1
        
        # Récupération robuste (transactions ou items)
        tx_list = data.get("transactions", data.get("items"))
        
        # On doit avoir nos 2 transactions
        assert len(tx_list) == 2
        
        # Vérification du format
        first_tx = tx_list[0]
        assert first_tx["id"].startswith("tx_")
        assert "amount" in first_tx
        assert "type" in first_tx

def test_get_transactions_filters_by_type():
    """Vérifie que le filtre ?type=TRANSFER fonctionne."""
    setup_mock_data()
    reset_deleted_ids()

    with TestClient(app) as client:
        # On demande SEULEMENT les TRANSFER
        r = client.get("/api/transactions?type=TRANSFER")
        assert r.status_code == 200
        data = r.json()
        
        tx_list = data.get("transactions", data.get("items"))
        
        # Il ne doit en rester qu'une seule
        assert len(tx_list) == 1
        assert tx_list[0]["type"] == "TRANSFER"