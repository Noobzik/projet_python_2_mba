"""
Tests de fonctionnalités avec unittest pour les clients.

Ce module contient des tests de features pour les clients.
"""

import unittest

from fastapi.testclient import TestClient

from banking_api.main import app


class TestCustomersFeatures(unittest.TestCase):
    """Tests de fonctionnalités pour les clients."""

    @classmethod
    def setUpClass(cls) -> None:
        """Configuration initiale de la classe de tests."""
        cls.client = TestClient(app)

    def test_customer_profile_data_consistency(self) -> None:
        """Test la cohérence des données du profil client."""
        # Récupérer un client
        list_response = self.client.get("/api/customers?limit=1")
        customers = list_response.json()["customers"]

        if customers:
            customer_id = customers[0]

            # Récupérer son profil
            profile_response = self.client.get(f"/api/customers/{customer_id}")
            self.assertEqual(profile_response.status_code, 200)
            profile = profile_response.json()

            # Vérifier que les montants sont cohérents
            if profile["transactions_count"] > 0:
                self.assertGreater(profile["avg_amount"], 0)
                self.assertGreater(profile["total_amount"], 0)
                # Le total doit être >= moyenne
                self.assertGreaterEqual(profile["total_amount"], profile["avg_amount"])

    def test_top_customers_are_sorted(self) -> None:
        """Test que les top clients sont triés correctement."""
        # Top par volume
        volume_response = self.client.get("/api/customers/top?n=10&by=volume")
        self.assertEqual(volume_response.status_code, 200)
        volume_customers = volume_response.json()

        # Vérifier le tri décroissant par total_amount
        for i in range(len(volume_customers) - 1):
            self.assertGreaterEqual(
                volume_customers[i]["total_amount"],
                volume_customers[i + 1]["total_amount"],
            )

        # Top par nombre
        count_response = self.client.get("/api/customers/top?n=10&by=count")
        self.assertEqual(count_response.status_code, 200)
        count_customers = count_response.json()

        # Vérifier le tri décroissant par transactions_count
        for i in range(len(count_customers) - 1):
            self.assertGreaterEqual(
                count_customers[i]["transactions_count"],
                count_customers[i + 1]["transactions_count"],
            )

    def test_top_customers_limit_respected(self) -> None:
        """Test que la limite du top clients est respectée."""
        for n in [5, 10, 20]:
            response = self.client.get(f"/api/customers/top?n={n}")
            self.assertEqual(response.status_code, 200)
            customers = response.json()
            self.assertLessEqual(len(customers), n)

    def test_customer_pagination_works(self) -> None:
        """Test que la pagination des clients fonctionne."""
        # Page 1
        response1 = self.client.get("/api/customers?page=1&limit=5")
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()

        # Page 2
        response2 = self.client.get("/api/customers?page=2&limit=5")
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()

        # Les clients doivent être différents
        if data1["customers"] and data2["customers"]:
            self.assertNotEqual(data1["customers"], data2["customers"])


if __name__ == "__main__":
    unittest.main()
