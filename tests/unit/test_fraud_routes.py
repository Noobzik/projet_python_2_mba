"""
Tests unitaires pour les routes de fraude.

Ce module teste tous les endpoints liés à la détection de fraude.
"""

from fastapi.testclient import TestClient

from banking_api.main import app

client: TestClient = TestClient(app)


class TestFraudRoutes:
    """Tests pour les routes de fraude."""

    def test_get_fraud_summary(self) -> None:
        """Test de récupération du résumé de fraude."""
        response = client.get("/api/fraud/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_frauds" in data
        assert "flagged" in data
        assert "precision" in data
        assert "recall" in data
        assert isinstance(data["total_frauds"], int)
        assert isinstance(data["precision"], (int, float))
        assert isinstance(data["recall"], (int, float))

    def test_get_fraud_by_type(self) -> None:
        """Test de récupération de la fraude par type."""
        response = client.get("/api/fraud/by-type")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Vérifier la structure
        if data:
            assert "type" in data[0]
            assert "fraud_count" in data[0]
            assert "total_count" in data[0]
            assert "fraud_rate" in data[0]

    def test_predict_fraud(self) -> None:
        """Test de prédiction de fraude."""
        prediction_request = {
            "amount": 1500.0,
            "use_chip": "Swipe Transaction",
            "merchant_state": "CA",
            "mcc": 5999,
        }
        response = client.post("/api/fraud/predict", json=prediction_request)
        assert response.status_code == 200
        data = response.json()
        assert "isFraud" in data
        assert "probability" in data
        assert isinstance(data["isFraud"], bool)
        assert 0.0 <= data["probability"] <= 1.0

    def test_predict_fraud_high_amount(self) -> None:
        """Test de prédiction avec montant élevé."""
        prediction_request = {
            "amount": 2000.0,
            "use_chip": "Swipe Transaction",
            "merchant_state": "TX",
            "mcc": 5944,
        }
        response = client.post("/api/fraud/predict", json=prediction_request)
        assert response.status_code == 200
        data = response.json()
        # Devrait avoir une probabilité élevée
        assert data["probability"] > 0.5
