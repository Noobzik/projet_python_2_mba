from fastapi.testclient import TestClient
from src.banking_api.main import app
from src.banking_api.models import TransactionSearch # Pour couvrir models.py
import pandas as pd

client = TestClient(app)

def test_health():
    """Test Route 19."""
    response = client.get("/api/system/health")
    assert response.status_code == 200

def test_models_coverage():
    """Force la couverture de models.py."""
    obj = TransactionSearch(type="TRANSFER")
    assert obj.type == "TRANSFER"

def test_stats_with_data():
    """
    Test Route 9 en simulant des données.
    Ceci va faire monter stats_service.py à 100%.
    """
    from src.banking_api.services.stats_service import get_global_stats
    fake_df = pd.DataFrame({
        'amount': [100, 200],
        'isFraud': [0, 1],
        'type': ['CASH_OUT', 'TRANSFER']
    })
    stats = get_global_stats(fake_df)
    assert "total_transactions" in stats
    assert stats["total_transactions"] == 2

def test_predict_fraud():
    """Test Route 15."""
    payload = {"type": "TRANSFER", "amount": 500000}
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 200
def test_stats_by_type():
    """Vérifie le calcul des statistiques par type (Route 11)."""
    from src.banking_api.services.stats_service import get_stats_by_type
    fake_df = pd.DataFrame({
        'type': ['TRANSFER', 'TRANSFER', 'CASH_OUT'],
        'amount': [100.0, 200.0, 50.0]
    })
    result = get_stats_by_type(fake_df)
    assert len(result) == 2  # TRANSFER et CASH_OUT
    # Vérifie que la moyenne pour TRANSFER est correcte (150.0)
    transfer_stats = next(item for item in result if item["type"] == "TRANSFER")
    assert transfer_stats["avg_amount"] == 150.0

