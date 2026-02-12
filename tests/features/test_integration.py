import unittest
import requests

class TestAPIIntegration(unittest.TestCase):
    """Tests d'intégration de l'API."""
    
    BASE_URL = "http://localhost:8000/api"
    
    def test_health_endpoint(self):
        """Test du endpoint health."""
        response = requests.get(f"{self.BASE_URL}/system/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
    
    def test_stats_overview(self):
        """Test du endpoint stats overview."""
        response = requests.get(f"{self.BASE_URL}/stats/overview")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_transactions", data)
    
    def test_transactions_list(self):
        """Test de la liste des transactions."""
        response = requests.get(f"{self.BASE_URL}/transactions?limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("transactions", data)

if __name__ == "__main__":
    unittest.main()
