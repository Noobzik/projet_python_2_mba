"""
Tests de fonctionnalités avec unittest pour le système.

Ce module contient des tests de features pour les endpoints système.
"""

import unittest

from fastapi.testclient import TestClient

from banking_api.main import app


class TestSystemFeatures(unittest.TestCase):
    """Tests de fonctionnalités pour le système."""

    @classmethod
    def setUpClass(cls) -> None:
        """Configuration initiale de la classe de tests."""
        cls.client = TestClient(app)

    def test_health_check_returns_valid_status(self) -> None:
        """Test que le health check retourne un statut valide."""
        response = self.client.get("/api/system/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Le statut doit être l'un des statuts valides
        valid_statuses = ["ok", "degraded", "error"]
        self.assertIn(data["status"], valid_statuses)

    def test_health_check_uptime_format(self) -> None:
        """Test que le format de l'uptime est correct."""
        response = self.client.get("/api/system/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # L'uptime doit contenir 'h' et 'min'
        self.assertIn("h", data["uptime"])
        self.assertIn("min", data["uptime"])

    def test_metadata_version_is_correct(self) -> None:
        """Test que la version dans les métadonnées est correcte."""
        response = self.client.get("/api/system/metadata")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # La version doit être "1.0.0"
        self.assertEqual(data["version"], "1.0.0")

    def test_metadata_has_transaction_count(self) -> None:
        """Test que les métadonnées incluent le nombre de transactions."""
        response = self.client.get("/api/system/metadata")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Le nombre de transactions doit être positif si les données sont chargées
        if data["total_transactions"] > 0:
            # Vérifier la cohérence avec l'overview
            overview_response = self.client.get("/api/stats/overview")
            overview = overview_response.json()
            self.assertEqual(data["total_transactions"], overview["total_transactions"])

    def test_root_endpoint_provides_documentation_link(self) -> None:
        """Test que l'endpoint racine fournit un lien vers la doc."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Doit contenir un lien vers la documentation
        self.assertIn("documentation", data)
        self.assertEqual(data["documentation"], "/docs")

    def test_api_is_responsive(self) -> None:
        """Test que l'API répond correctement."""
        endpoints = [
            "/",
            "/api/system/health",
            "/api/system/metadata",
            "/api/stats/overview",
            "/api/transactions/types",
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
