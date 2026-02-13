"""Tests fonctionnels pour les routes client.

Ce module teste les endpoints API client (Routes 16-18).
"""

import unittest

from fastapi.testclient import TestClient

from banking_api.main import app


class TestCustomersRoutes(unittest.TestCase):
    """Suite de tests pour les routes client."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialiser le client de test pour tous les tests."""
        cls.client = TestClient(app)

    def test_get_customers_paginated(self) -> None:
        """Tester GET /api/customers avec pagination."""
        response = self.client.get("/api/customers?page=1&limit=10")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("page", data)
        self.assertIn("customers", data)
        self.assertIn("total", data)

    def test_get_customers_pagination_values(self) -> None:
        """Tester les valeurs de pagination des clients."""
        response = self.client.get("/api/customers?page=1&limit=5")
        data = response.json()

        self.assertEqual(data["page"], 1)
        self.assertEqual(data["limit"], 5)
        self.assertLessEqual(len(data["customers"]), 5)

    def test_get_customer_profile(self) -> None:
        """Tester GET /api/customers/{customer_id}."""
        response = self.client.get("/api/customers")
        customers_data = response.json()

        if len(customers_data["customers"]) > 0:
            customer_id = customers_data["customers"][0]
            profile_response = self.client.get(f"/api/customers/{customer_id}")

            self.assertEqual(profile_response.status_code, 200)
            profile = profile_response.json()
            self.assertIn("id", profile)
            self.assertIn("transactions_count", profile)
            self.assertIn("avg_amount", profile)

    def test_get_customer_profile_not_found(self) -> None:
        """Tester GET /api/customers/{customer_id} avec un identifiant invalide."""
        response = self.client.get("/api/customers/NONEXISTENT_CUSTOMER")

        self.assertEqual(response.status_code, 404)

    def test_customer_profile_structure(self) -> None:
        """Tester la structure des données du profil client."""
        response = self.client.get("/api/customers")
        customers_data = response.json()

        if len(customers_data["customers"]) > 0:
            customer_id = customers_data["customers"][0]
            profile_response = self.client.get(f"/api/customers/{customer_id}")
            profile = profile_response.json()

            self.assertIn("id", profile)
            self.assertIn("transactions_count", profile)
            self.assertIn("avg_amount", profile)
            self.assertIn("total_amount", profile)
            self.assertIn("fraudulent", profile)
            self.assertIn("fraud_count", profile)

    def test_get_top_customers(self) -> None:
        """Tester GET /api/customers/top."""
        response = self.client.get("/api/customers/top?n=5")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 5)

    def test_top_customers_structure(self) -> None:
        """Tester la structure des données des meilleurs clients."""
        response = self.client.get("/api/customers/top?n=3")
        data = response.json()

        if len(data) > 0:
            for customer in data:
                self.assertIn("customer_id", customer)
                self.assertIn("total_volume", customer)
                self.assertIn("transaction_count", customer)

    def test_top_customers_sorted(self) -> None:
        """Tester que les meilleurs clients sont triés par volume décroissant."""
        response = self.client.get("/api/customers/top?n=5")
        data = response.json()

        if len(data) > 1:
            volumes = [c["total_volume"] for c in data]
            self.assertEqual(volumes, sorted(volumes, reverse=True))

    def test_top_customers_limit(self) -> None:
        """Tester que la limite du nombre de meilleurs clients est respectée."""
        response = self.client.get("/api/customers/top?n=3")
        data = response.json()

        self.assertLessEqual(len(data), 3)


if __name__ == "__main__":
    unittest.main()
