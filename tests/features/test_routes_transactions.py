"""Tests fonctionnels pour les routes des transactions.

Ce module teste les endpoints API des transactions (Routes 1-8).
"""

import unittest

from fastapi.testclient import TestClient

from banking_api.main import app


class TestTransactionsRoutes(unittest.TestCase):
    """Suite de tests pour les routes des transactions."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialiser le client de test pour tous les tests."""
        cls.client = TestClient(app)

    def test_get_transactions_paginated(self) -> None:
        """Tester GET /api/transactions avec pagination."""
        response = self.client.get("/api/transactions?page=1&limit=10")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("page", data)
        self.assertIn("transactions", data)
        self.assertEqual(data["page"], 1)

    def test_get_transactions_with_filters(self) -> None:
        """Tester GET /api/transactions avec filtres."""
        response = self.client.get("/api/transactions?type=PAYMENT&limit=5")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("transactions", data)

    def test_get_transaction_by_id(self) -> None:
        """Tester GET /api/transactions/{id}."""
        response = self.client.get("/api/transactions/tx_0")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], "tx_0")
        self.assertIn("type", data)
        self.assertIn("amount", data)

    def test_get_transaction_by_id_not_found(self) -> None:
        """Tester GET /api/transactions/{id} avec identifiant invalide."""
        response = self.client.get("/api/transactions/tx_99999999999")

        self.assertEqual(response.status_code, 404)

    def test_post_search_transactions(self) -> None:
        """Tester POST /api/transactions/search."""
        search_data = {"type": "TRANSFER", "isFraud": 0}
        response = self.client.post("/api/transactions/search", json=search_data)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_post_search_with_amount_range(self) -> None:
        """Tester POST /api/transactions/search avec intervalle de montant."""
        search_data = {"amount_range": [1000.0, 10000.0]}
        response = self.client.post("/api/transactions/search", json=search_data)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_get_transaction_types(self) -> None:
        """Tester GET /api/transactions/types."""
        response = self.client.get("/api/transactions/types")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_get_recent_transactions(self) -> None:
        """Tester GET /api/transactions/recent."""
        response = self.client.get("/api/transactions/recent?n=5")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 5)

    def test_delete_transaction(self) -> None:
        """Tester DELETE /api/transactions/{id}."""
        response = self.client.delete("/api/transactions/tx_0")

        self.assertEqual(response.status_code, 204)

    def test_delete_transaction_not_found(self) -> None:
        """Tester DELETE /api/transactions/{id} avec identifiant invalide."""
        response = self.client.delete("/api/transactions/tx_99999999999")

        self.assertEqual(response.status_code, 404)

    def test_get_transactions_by_customer(self) -> None:
        """Tester GET /api/transactions/by-customer/{customer_id}."""
        response = self.client.get("/api/transactions/by-customer/C1231006815")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_get_transactions_to_customer(self) -> None:
        """Tester GET /api/transactions/to-customer/{customer_id}."""
        response = self.client.get("/api/transactions/to-customer/C1231006815")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)


if __name__ == "__main__":
    unittest.main()
