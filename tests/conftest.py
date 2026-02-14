import pytest
import pandas as pd
from fastapi.testclient import TestClient
from banking_api.main import app
from banking_api.services import dataset_loader

# --- 1. CRÉATION DU FAUX DATASET (MOCK) ---
# On crée un petit DataFrame de test qui ressemble exactement au vrai
@pytest.fixture(scope="session", autouse=True)
def mock_dataset():
    """
    Remplace le chargement Kaggle par un petit DataFrame en mémoire.
    Cela rend les tests ultra-rapides (0.1 seconde).
    """
    data = {
        "step": [1, 1, 2, 2, 3],
        "type": ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "TRANSFER"],
        "amount": [10.50, 250000.00, 50.00, 15.00, 1000.00],
        "nameOrig": ["C1001", "C1002", "C1003", "C1004", "C1005"],
        "oldbalanceOrg": [100.0, 250000.0, 50.0, 200.0, 1000.0],
        "newbalanceOrig": [89.5, 0.0, 0.0, 185.0, 0.0],
        "nameDest": ["M2001", "C3002", "C3003", "M2004", "C3005"],
        "oldbalanceDest": [0.0, 0.0, 0.0, 0.0, 0.0],
        "newbalanceDest": [0.0, 0.0, 0.0, 0.0, 0.0],
        "isFraud": [0, 1, 0, 0, 0], # On met une fraude explicite
        "isFlaggedFraud": [0, 0, 0, 0, 0]
    }
    df = pd.DataFrame(data)
    
    # On force les types comme dans le vrai loader
    df['step'] = df['step'].astype('int32')
    df['amount'] = df['amount'].astype('float32')
    df['isFraud'] = df['isFraud'].astype('int8')
    
    # --- LA MAGIE DU MOCK ---
    # On remplace la variable cache du loader par notre petit DF
    dataset_loader._DATAFRAME_CACHE = df
    dataset_loader._CURRENT_PATH = "MOCK_DATASET_FOR_TESTS"
    
    return df

# --- 2. CLIENT DE TEST ---
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c