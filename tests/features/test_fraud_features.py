"""
Tests de fonctionnalités avec unittest pour la fraude.

Ce module contient des tests de features pour la détection de fraude.
"""

import unittest

from fastapi.testclient import TestClient

from banking_api.main import app


class TestFraudFeatures(unittest.TestCase):
    """Tests de fonctionnalités pour la détection de fraude."""

    @classmethod
    def setUpClass(cls) -> None:
        """Configuration initiale de la classe de tests."""
        cls.client = TestClient(app)

    def test_fraud_summary_metrics_are_valid(self) -> None:
        """Test que les métriques de fraude sont valides."""
        response = self.client.get("/api/fraud/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Précision et rappel doivent être entre 0 et 1
        self.assertGreaterEqual(data["precision"], 0.0)
        self.assertLessEqual(data["precision"], 1.0)
        self.assertGreaterEqual(data["recall"], 0.0)
        self.assertLessEqual(data["recall"], 1.0)

        # Le nombre de fraudes signalées ne peut pas dépasser le total
        self.assertLessEqual(data["flagged"], data["total_frauds"])

    def test_fraud_by_type_rates_are_valid(self) -> None:
        """Test que les taux de fraude par type sont valides."""
        response = self.client.get("/api/fraud/by-type")
        self.assertEqual(response.status_code, 200)
        fraud_stats = response.json()

        for stat in fraud_stats:
            # Le taux de fraude doit être entre 0 et 1
            self.assertGreaterEqual(stat["fraud_rate"], 0.0)
            self.assertLessEqual(stat["fraud_rate"], 1.0)

            # Le nombre de fraudes ne peut pas dépasser le total
            self.assertLessEqual(stat["fraud_count"], stat["total_count"])

    def test_fraud_prediction_low_risk_transaction(self) -> None:
        """Test de prédiction pour une transaction à faible risque."""
        prediction_request = {
            "amount": 50.0,
            "use_chip": "Chip Transaction",
            "merchant_state": "WA",
            "mcc": 5411,
        }
        response = self.client.post("/api/fraud/predict", json=prediction_request)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Devrait avoir une faible probabilité
        self.assertLess(data["probability"], 0.5)

    def test_fraud_prediction_high_risk_transaction(self) -> None:
        """Test de prédiction pour une transaction à haut risque."""
        prediction_request = {
            "amount": 2500.0,
            "use_chip": "Swipe Transaction",
            "merchant_state": "CA",
            "mcc": 5944,
        }
        response = self.client.post("/api/fraud/predict", json=prediction_request)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Devrait avoir une probabilité élevée
        self.assertGreaterEqual(data["probability"], 0.5)
        self.assertTrue(data["isFraud"])

    def test_fraud_prediction_probability_bounds(self) -> None:
        """Test que la probabilité est toujours entre 0 et 1."""
        test_cases = [
            {
                "amount": 100.0,
                "use_chip": "Chip Transaction",
                "merchant_state": "OR",
                "mcc": 5812,
            },
            {
                "amount": 1500.0,
                "use_chip": "Swipe Transaction",
                "merchant_state": "TX",
                "mcc": 5999,
            },
            {
                "amount": 25.0,
                "use_chip": "Online Transaction",
                "merchant_state": "WA",
                "mcc": 5411,
            },
        ]

        for test_case in test_cases:
            response = self.client.post("/api/fraud/predict", json=test_case)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertGreaterEqual(data["probability"], 0.0)
            self.assertLessEqual(data["probability"], 1.0)


if __name__ == "__main__":
    unittest.main()
