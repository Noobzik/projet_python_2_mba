"""Tests unittest pour le service de détection de fraude."""
import unittest
import os
import tempfile
import pandas as pd
from unittest.mock import patch
from banking_api.services import fraud_detection_service


class TestFraudDetectionService(unittest.TestCase):
    """Tests pour le service de détection de fraude."""

    @classmethod
    def setUpClass(cls):
        """Configuration avant tous les tests."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.csv_path = os.path.join(cls.temp_dir, 'transactions_data.csv')

        # Créer données de test
        data = {
            'step': [1, 1, 2, 2, 3],
            'type': ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT', 'PAYMENT'],
            'amount': [9839.64, 181.00, 181.00, 52.95, 1234.56],
            'nameOrig': ['C1231006815', 'C1666544295', 'C1305486145', 'C840083671', 'C1231006815'],
            'oldbalanceOrg': [170136.00, 181.00, 181.00, 41720.00, 168902.36],
            'newbalanceOrig': [160296.36, 0.00, 0.00, 41667.05, 167667.80],
            'nameDest': ['M1979787155', 'C1900366749', 'C840083671', 'C1634788479', 'M1234567890'],
            'oldbalanceDest': [0.00, 0.00, 21182.00, 41898.00, 0.00],
            'newbalanceDest': [0.00, 0.00, 21182.00, 41950.95, 0.00],
            'isFraud': [0, 1, 0, 0, 0],
            'isFlaggedFraud': [0, 0, 0, 0, 0]
        }
        df = pd.DataFrame(data)
        df.to_csv(cls.csv_path, index=False)

    def setUp(self):
        """Configuration avant chaque test."""
        self.patcher = patch.object(
            fraud_detection_service,
            '_get_csv_path',
            return_value=self.csv_path)
        self.patcher.start()

    def tearDown(self):
        """Nettoyage après chaque test."""
        self.patcher.stop()

    def test_get_fraud_summary(self):
        """Test du résumé de fraude."""
        summary = fraud_detection_service.get_fraud_summary()

        self.assertIn('total_frauds', summary)
        self.assertIn('flagged', summary)
        self.assertIn('precision', summary)
        self.assertIn('recall', summary)

        self.assertEqual(summary['total_frauds'], 1)
        self.assertGreaterEqual(summary['precision'], 0)
        self.assertLessEqual(summary['precision'], 1)
        self.assertGreaterEqual(summary['recall'], 0)
        self.assertLessEqual(summary['recall'], 1)

    def test_get_fraud_by_type(self):
        """Test de la fraude par type."""
        fraud_stats = fraud_detection_service.get_fraud_by_type()

        self.assertIsInstance(fraud_stats, list)
        self.assertEqual(len(fraud_stats), 4)

        for stat in fraud_stats:
            self.assertIn('type', stat)
            self.assertIn('total_transactions', stat)
            self.assertIn('fraud_count', stat)
            self.assertIn('fraud_rate', stat)
            self.assertGreater(stat['total_transactions'], 0)
            self.assertGreaterEqual(stat['fraud_count'], 0)
            self.assertGreaterEqual(stat['fraud_rate'], 0)
            self.assertLessEqual(stat['fraud_rate'], 100)

    def test_predict_fraud_high_amount_transfer(self):
        """Test de prédiction pour montant élevé."""
        prediction = fraud_detection_service.predict_fraud(
            transaction_type='TRANSFER',
            amount=250000,
            oldbalance_org=250000,
            newbalance_orig=0
        )

        self.assertIn('isFraud', prediction)
        self.assertIn('probability', prediction)
        self.assertIn('reasons', prediction)
        self.assertTrue(prediction['isFraud'])
        self.assertGreater(prediction['probability'], 0.5)

    def test_predict_fraud_normal_payment(self):
        """Test de prédiction pour paiement normal."""
        prediction = fraud_detection_service.predict_fraud(
            transaction_type='PAYMENT',
            amount=100,
            oldbalance_org=1000,
            newbalance_orig=900
        )

        self.assertFalse(prediction['isFraud'])
        self.assertLess(prediction['probability'], 0.5)

    def test_predict_fraud_account_emptying(self):
        """Test pour vidage de compte."""
        prediction = fraud_detection_service.predict_fraud(
            transaction_type='CASH_OUT',
            amount=10000,
            oldbalance_org=10000,
            newbalance_orig=0
        )

        self.assertGreater(prediction['probability'], 0)

    def test_predict_fraud_probability_capped(self):
        """Test que la probabilité est plafonnée à 1.0."""
        prediction = fraud_detection_service.predict_fraud(
            transaction_type='TRANSFER',
            amount=500000,
            oldbalance_org=500000,
            newbalance_orig=10
        )

        self.assertLessEqual(prediction['probability'], 1.0)

    def test_predict_fraud_reasons_provided(self):
        """Test que des raisons sont fournies."""
        prediction = fraud_detection_service.predict_fraud(
            transaction_type='TRANSFER',
            amount=300000,
            oldbalance_org=300000,
            newbalance_orig=0
        )

        self.assertIsInstance(prediction['reasons'], list)
        self.assertGreater(len(prediction['reasons']), 0)


if __name__ == '__main__':
    unittest.main()
