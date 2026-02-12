"""Tests fonctionnels pour les routes système.

Ce module teste les endpoints API système (Routes 19-20).
"""
import unittest
from fastapi.testclient import TestClient
from banking_api.main import app


class TestSystemRoutes(unittest.TestCase):
    """Suite de tests pour les routes système."""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Initialiser le client de test pour tous les tests."""
        cls.client = TestClient(app)
    
    def test_get_health(self) -> None:
        """Tester GET /api/system/health."""
        response = self.client.get("/api/system/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('uptime', data)
        self.assertIn('dataset_loaded', data)
        self.assertIn('total_records', data)
    
    def test_health_status_values(self) -> None:
        """Tester les valeurs du statut du contrôle de santé."""
        response = self.client.get("/api/system/health")
        data = response.json()
        
        self.assertIn(data['status'], ['ok', 'degraded', 'error'])
        self.assertIsInstance(data['dataset_loaded'], bool)
        self.assertGreaterEqual(data['total_records'], 0)
    
    def test_health_uptime_format(self) -> None:
        """Tester le format du temps de fonctionnement dans le contrôle de santé."""
        response = self.client.get("/api/system/health")
        data = response.json()
        
        self.assertIsInstance(data['uptime'], str)
        self.assertGreater(len(data['uptime']), 0)
    
    def test_get_metadata(self) -> None:
        """Tester GET /api/system/metadata."""
        response = self.client.get("/api/system/metadata")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('version', data)
        self.assertIn('last_update', data)
        self.assertIn('total_endpoints', data)
        self.assertIn('dataset_info', data)
    
    def test_metadata_version(self) -> None:
        """Tester les informations de version dans les métadonnées."""
        response = self.client.get("/api/system/metadata")
        data = response.json()
        
        self.assertEqual(data['version'], '1.0.0')
        self.assertIsInstance(data['last_update'], str)
    
    def test_metadata_endpoints_count(self) -> None:
        """Tester le nombre d’endpoints dans les métadonnées."""
        response = self.client.get("/api/system/metadata")
        data = response.json()
        
        self.assertEqual(data['total_endpoints'], 20)
    
    def test_metadata_dataset_info(self) -> None:
        """Tester les informations du dataset dans les métadonnées."""
        response = self.client.get("/api/system/metadata")
        data = response.json()
        
        self.assertIsInstance(data['dataset_info'], dict)
        self.assertIn('records', data['dataset_info'])
        self.assertGreater(data['dataset_info']['records'], 0)
    
    def test_root_endpoint(self) -> None:
        """Tester GET / endpoint racine."""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('version', data)
    
    def test_docs_endpoint_accessible(self) -> None:
        """Tester que l’endpoint /docs est accessible."""
        response = self.client.get("/docs")
        
        self.assertEqual(response.status_code, 200)
    
    def test_redoc_endpoint_accessible(self) -> None:
        """Tester que l’endpoint /redoc est accessible."""
        response = self.client.get("/redoc")
        
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()