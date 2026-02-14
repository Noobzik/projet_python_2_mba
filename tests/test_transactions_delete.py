from __future__ import annotations
import pandas as pd
from fastapi.testclient import TestClient
from banking_api.main import app
from banking_api.services import dataset_loader
from banking_api.services.transactions_service import reset_deleted_ids

# --- 1. SETUP DES DONNÉES (MOCK) ---
def setup_mock_data():
    """
    On injecte 2 transactions simples pour tester la suppression.
    L'index 0 sera 'tx_0000000' et l'index 1 sera 'tx_0000001'.
    """
    df = pd.DataFrame([
        # Transaction 0 (tx_0000000)
        {
            "step": 1, "type": "TRANSFER", "amount": 100.0, 
            "nameOrig": "C1", "nameDest": "C2", 
            "isFraud": 0, "isFlaggedFraud": 0,
            "oldbalanceOrg": 0, "newbalanceOrig": 0, "oldbalanceDest": 0, "newbalanceDest": 0
        },
        # Transaction 1 (tx_0000001)
        {
            "step": 1, "type": "CASH_OUT", "amount": 200.0, 
            "nameOrig": "C1", "nameDest": "C3", 
            "isFraud": 0, "isFlaggedFraud": 0,
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

def test_delete_transaction_forbidden_in_dev(monkeypatch):
    """
    Vérifie qu'on ne peut PAS supprimer une transaction en mode 'dev'.
    """
    setup_mock_data()
    reset_deleted_ids() # Important : On remet la liste des suppressions à zéro
    
    # On force l'environnement à "dev"
    monkeypatch.setenv("APP_ENV", "dev")

    with TestClient(app) as client:
        # On essaie de supprimer la transaction 0
        r = client.delete("/api/transactions/tx_0000000")
        
        # Ça doit être interdit (403 Forbidden)
        assert r.status_code == 403

def test_delete_transaction_allowed_in_test_and_excluded(monkeypatch):
    """
    Vérifie qu'on PEUT supprimer en mode 'test' et qu'elle disparaît de la liste.
    """
    setup_mock_data()
    reset_deleted_ids() # On repart à zéro
    
    # On force l'environnement à "test" (seul mode qui autorise la suppression)
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(app) as client:
        # 1. Suppression de la transaction 0
        r = client.delete("/api/transactions/tx_0000000")
        assert r.status_code == 204 # 204 No Content = Succès

        # 2. Vérification : La liste ne doit plus contenir que la transaction 1
        r2 = client.get("/api/transactions?page=1&limit=10")
        assert r2.status_code == 200
        data = r2.json()
        
        # Gestion flexible de la réponse (items ou transactions)
        tx_list = data.get("items", data.get("transactions"))
        
        # Il ne doit en rester qu'une
        assert len(tx_list) == 1
        # Celle qui reste doit être tx_0000001
        assert tx_list[0]["id"] == "tx_0000001"