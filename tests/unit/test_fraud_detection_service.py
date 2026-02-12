"""
Tests unitaires pour le service de détection de fraude.
"""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from banking_api.models.schemas import FraudPredictionRequest, FraudSummary
from banking_api.services.fraud_detection_service import FraudDetectionService


class TestFraudDetectionService(unittest.TestCase):
    """Tests pour le service de détection de fraude."""

    def setUp(self) -> None:
        """Configuration initiale des tests."""
        self.mock_data_loader = MagicMock()

        # Créer un DataFrame de test
        data = {
            "amount": [100.0, 600.0, 200.0, 1200.0, 50.0],
            "use_chip": [
                "Chip Transaction",
                "Swipe Transaction",
                "Online Transaction",
                "Swipe Transaction",
                "Chip Transaction",
            ],
            "errors": [None, "Bad PIN", None, "Insufficient Balance", None],
            "merchant_state": ["CA", "NY", "TX", "FL", "CA"],
            "mcc": [5000, 5944, 5000, 5732, 5000],
        }
        self.test_df = pd.DataFrame(data)

        # Patcher le data_loader dans le service
        self.patcher = patch(
            "banking_api.services.fraud_detection_service.data_loader",
            self.mock_data_loader,
        )
        self.patcher.start()

        self.fraud_service = FraudDetectionService()
        self.mock_data_loader.get_transactions.return_value = self.test_df

    def tearDown(self) -> None:
        """Nettoyage après les tests."""
        self.patcher.stop()

    def test_get_fraud_summary(self) -> None:
        """Test du résumé de fraude."""
        summary = self.fraud_service.get_fraud_summary()

        self.assertIsInstance(summary, FraudSummary)
        self.assertEqual(summary.total_frauds, 2)  # 2 erreurs
        self.assertEqual(summary.flagged, 1)  # 1 "Bad PIN" qui contient "Bad"
        # Precision: 1 / (1 + 0) = 1.0
        self.assertEqual(summary.precision, 1.0)
        # Recall: 1 / (1 + 1) = 0.5
        self.assertEqual(summary.recall, 0.5)

    def test_get_fraud_by_type(self) -> None:
        """Test de la fraude par type."""
        fraud_by_type = self.fraud_service.get_fraud_by_type()

        self.assertIsInstance(fraud_by_type, list)
        self.assertEqual(len(fraud_by_type), 3)  # Chip, Swipe, Online

        # Swipe Transaction: 2 trans, 2 frauds -> 100%
        swipe = next((f for f in fraud_by_type if f.type == "Swipe Transaction"), None)
        self.assertIsNotNone(swipe)
        if swipe:
            self.assertEqual(swipe.fraud_rate, 1.0)

    def test_predict_fraud(self) -> None:
        """Test de prédiction de fraude."""
        # Cas normal
        req_normal = FraudPredictionRequest(
            amount=100.0, use_chip="Chip Transaction", merchant_state="CA", mcc=5000
        )
        resp_normal = self.fraud_service.predict_fraud(req_normal)
        self.assertFalse(resp_normal.isFraud)
        self.assertEqual(resp_normal.probability, 0.1)  # CA risk +0.1

        # Cas fraude (montant élevé, swipe, state risk, mcc risk)
        req_fraud = FraudPredictionRequest(
            amount=1500.0, use_chip="Swipe Transaction", merchant_state="NY", mcc=5944
        )
        resp_fraud = self.fraud_service.predict_fraud(req_fraud)
        self.assertTrue(resp_fraud.isFraud)
        # Score: 0.3 (>500) + 0.2 (>1000) + 0.3 (Swipe) + 0.1 (NY) + 0.1 (MCC) = 1.0
        self.assertEqual(resp_fraud.probability, 1.0)

    def test_get_fraud_patterns(self) -> None:
        """Test des patterns de fraude."""
        patterns = self.fraud_service.get_fraud_patterns()

        self.assertEqual(patterns["total_fraud_amount"], 1800.0)  # 600 + 1200
        self.assertEqual(patterns["max_fraud_amount"], 1200.0)
        self.assertEqual(patterns["most_common_fraud_type"], "Swipe Transaction")

    def test_get_fraud_patterns_no_fraud(self) -> None:
        """Test des patterns sans fraude."""
        self.mock_data_loader.get_transactions.return_value = pd.DataFrame(
            {"amount": [100.0], "use_chip": ["Chip"], "errors": [None]}
        )

        patterns = self.fraud_service.get_fraud_patterns()
        self.assertEqual(patterns["total_fraud_amount"], 0.0)

    def test_get_high_risk_transactions(self) -> None:
        """Test des transactions à haut risque."""
        # Le DataFrame de test a déjà des transactions qui devraient être flaggées
        # ID 1 (600, Swipe, Bad PIN) -> Risk: 0.3 (>500) + 0.3 (Swipe) + 0.4 (Error) = 1.0
        # ID 3 (1200, Swipe, Insufficient) -> Risk: 0.3 + 0.2 + 0.3 + 0.4 = 1.2 -> 1.0

        high_risk = self.fraud_service.get_high_risk_transactions(threshold=0.8)
        self.assertEqual(len(high_risk), 2)

        # Vérifier que les montants correspondent
        amounts = [t["amount"] for t in high_risk]
        self.assertIn(600.0, amounts)
        self.assertIn(1200.0, amounts)
