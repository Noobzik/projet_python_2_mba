"""Tests fonctionnels pour les routes de statistiques.

Ce module teste les endpoints API de statistiques (Routes 9-12).
"""
import unittest
from fastapi.testclient import TestClient
from banking_api.main import app


class TestStatsRoutes(unittest.TestCase):
    """Suite de tests pour les routes de statistiques."""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Initialiser le client de test pour tous les tests."""
        cls.client = TestClient(app)
    
    def test_get_stats_overview(self) -> None:
        """Tester GET /api/stats/overview."""
        response = self.client.get("/api/stats/overview")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_transactions', data)
        self.assertIn('fraud_rate', data)
        self.assertIn('avg_amount', data)
        self.assertIn('most_common_type', data)
    
    def test_stats_overview_values(self) -> None:
        """Tester que les statistiques globales ont des valeurs valides."""
        response = self.client.get("/api/stats/overview")
        data = response.json()
        
        self.assertGreater(data['total_transactions'], 0)
        self.assertGreaterEqual(data['fraud_rate'], 0)
        self.assertLessEqual(data['fraud_rate'], 1)
        self.assertGreater(data['avg_amount'], 0)
    
    def test_get_amount_distribution(self) -> None:
        """Tester GET /api/stats/amount-distribution."""
        response = self.client.get("/api/stats/amount-distribution")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('bins', data)
        self.assertIn('counts', data)
        self.assertEqual(len(data['bins']), len(data['counts']))
    
    def test_amount_distribution_bins(self) -> None:
        """Tester que les classes de distribution des montants sont correctes."""
        response = self.client.get("/api/stats/amount-distribution")
        data = response.json()
        
        self.assertIsInstance(data['bins'], list)
        self.assertIsInstance(data['counts'], list)
        self.assertGreater(len(data['bins']), 0)
    
    def test_get_stats_by_type(self) -> None:
        """Tester GET /api/stats/by-type."""
        response = self.client.get("/api/stats/by-type")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_stats_by_type_structure(self) -> None:
        """Tester la structure des statistiques par type."""
        response = self.client.get("/api/stats/by-type")
        data = response.json()
        
        for stat in data:
            self.assertIn('type', stat)
            self.assertIn('count', stat)
            self.assertIn('avg_amount', stat)
            self.assertIn('total_amount', stat)
    
    def test_get_daily_stats(self) -> None:
        """Tester GET /api/stats/daily."""
        response = self.client.get("/api/stats/daily")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_daily_stats_structure(self) -> None:
        """Tester la structure des statistiques journalières."""
        response = self.client.get("/api/stats/daily")
        data = response.json()
        
        if len(data) > 0:
            first_stat = data[0]
            self.assertIn('step', first_stat)
            self.assertIn('count', first_stat)
            self.assertIn('avg_amount', first_stat)
            self.assertIn('total_amount', first_stat)


if __name__ == '__main__':
    unittest.main()