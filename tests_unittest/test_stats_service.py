"""Tests unittest pour le service de statistiques."""
import unittest
import os
import tempfile
import pandas as pd
from unittest.mock import patch
from banking_api.services import stats_service


class TestStatsService(unittest.TestCase):
    """Tests pour le service de statistiques."""

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
        self.patcher = patch.object(stats_service, '_get_csv_path', return_value=self.csv_path)
        self.patcher.start()

    def tearDown(self):
        """Nettoyage après chaque test."""
        self.patcher.stop()

    def test_get_overview(self):
        """Test des statistiques globales."""
        overview = stats_service.get_overview()

        self.assertIn('total_transactions', overview)
        self.assertIn('fraud_rate', overview)
        self.assertIn('avg_amount', overview)
        self.assertIn('most_common_type', overview)

        self.assertEqual(overview['total_transactions'], 5)
        self.assertGreaterEqual(overview['fraud_rate'], 0)
        self.assertLessEqual(overview['fraud_rate'], 1)
        self.assertGreater(overview['avg_amount'], 0)

    def test_get_amount_distribution(self):
        """Test de la distribution des montants."""
        distribution = stats_service.get_amount_distribution(bins=10)

        self.assertIn('bins', distribution)
        self.assertIn('counts', distribution)
        self.assertIsInstance(distribution['bins'], list)
        self.assertIsInstance(distribution['counts'], list)
        self.assertEqual(len(distribution['bins']), len(distribution['counts']))

    def test_get_stats_by_type(self):
        """Test des statistiques par type."""
        stats = stats_service.get_stats_by_type()

        self.assertIsInstance(stats, list)
        self.assertEqual(len(stats), 4)

        for stat in stats:
            self.assertIn('type', stat)
            self.assertIn('count', stat)
            self.assertIn('avg_amount', stat)
            self.assertIn('total_amount', stat)
            self.assertGreater(stat['count'], 0)
            self.assertGreater(stat['avg_amount'], 0)

    def test_get_daily_stats(self):
        """Test des statistiques quotidiennes."""
        daily = stats_service.get_daily_stats()

        self.assertIsInstance(daily, list)
        self.assertEqual(len(daily), 3)

        for day_stat in daily:
            self.assertIn('day', day_stat)
            self.assertIn('count', day_stat)
            self.assertIn('avg_amount', day_stat)
            self.assertIn('total_amount', day_stat)
            self.assertGreater(day_stat['count'], 0)

    def test_get_daily_stats_order(self):
        """Test que les stats sont ordonnées."""
        daily = stats_service.get_daily_stats()

        days = [d['day'] for d in daily]
        self.assertEqual(days, sorted(days))


if __name__ == '__main__':
    unittest.main()
