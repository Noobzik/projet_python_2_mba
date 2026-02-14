from __future__ import annotations
import pandas as pd
from fastapi.testclient import TestClient
from banking_api.main import app
from banking_api.services import dataset_loader

def setup_mock_data():
    df = pd.DataFrame([
        {"step": 1, "type": "TRANSFER", "amount": 100.0, "nameOrig": "C1", "nameDest": "C2", "isFraud": 0, "isFlaggedFraud": 0, "oldbalanceOrg": 0, "newbalanceOrig": 0, "oldbalanceDest": 0, "newbalanceDest": 0},
        {"step": 2, "type": "CASH_OUT", "amount": 500.0, "nameOrig": "C2", "nameDest": "C3", "isFraud": 1, "isFlaggedFraud": 0, "oldbalanceOrg": 0, "newbalanceOrig": 0, "oldbalanceDest": 0, "newbalanceDest": 0},
        {"step": 3, "type": "TRANSFER", "amount": 200.0, "nameOrig": "C3", "nameDest": "C4", "isFraud": 0, "isFlaggedFraud": 0, "oldbalanceOrg": 0, "newbalanceOrig": 0, "oldbalanceDest": 0, "newbalanceDest": 0},
    ])
    df['step'] = df['step'].astype('int32')
    df['amount'] = df['amount'].astype('float32')
    df['isFraud'] = df['isFraud'].astype('int8')
    dataset_loader._DATAFRAME_CACHE = df
    return df

def test_get_transaction_by_id():
    setup_mock_data()
    with TestClient(app) as client:
        r = client.get("/api/transactions/tx_0000001")
        assert r.status_code == 200
        assert r.json()["id"] == "tx_0000001"

def test_get_transaction_by_id_not_found():
    setup_mock_data()
    with TestClient(app) as client:
        r = client.get("/api/transactions/tx_9999999")
        assert r.status_code == 404

def test_get_transaction_types():
    """Vérifie la liste des types."""
    setup_mock_data()
    with TestClient(app) as client:
        r = client.get("/api/transactions/types")
        assert r.status_code == 200
        data = r.json()
        
        # CORRECTION : Gestion si c'est une liste directe
        if isinstance(data, list):
            types_list = data
        else:
            types_list = data.get("items", data)
        
        assert "TRANSFER" in types_list
        assert "CASH_OUT" in types_list

def test_get_recent_transactions():
    setup_mock_data()
    with TestClient(app) as client:
        r = client.get("/api/transactions/recent?n=2")
        assert r.status_code == 200
        data = r.json()
        if isinstance(data, list):
            recent_list = data
        else:
            recent_list = data.get("items", data.get("transactions"))
        assert len(recent_list) == 2