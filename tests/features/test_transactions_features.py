"""
Tests de fonctionnalités avec unittest pour les transactions.

Ce module contient des tests de features pour les transactions.
"""

import unittest

from fastapi.testclient import TestClient

from banking_api.main import app


class TestTransactionsFeatures(unittest.TestCase):
    """Tests de fonctionnalités pour les transactions."""

    @classmethod
    def setUpClass(cls) -> None:
        """Configuration initiale de la classe de tests."""
        cls.client = TestClient(app)

    def test_pagination_works_correctly(self) -> None:
        """Test que la pagination fonctionne correctement."""
        # Page 1
        response1 = self.client.get("/api/transactions?page=1&limit=10")
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()

        # Page 2
        response2 = self.client.get("/api/transactions?page=2&limit=10")
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()

        # Les transactions doivent être différentes
        if data1["transactions"] and data2["transactions"]:
            self.assertNotEqual(
                data1["transactions"][0]["id"], data2["transactions"][0]["id"]
            )

    def test_fraud_filter_works(self) -> None:
        """Test que le filtre de fraude fonctionne."""
        response = self.client.get("/api/transactions?has_errors=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Toutes les transactions doivent avoir des erreurs (errors non nul)
        for transaction in data["transactions"]:
            self.assertIsNotNone(transaction.get("errors"))

    def test_amount_range_filter(self) -> None:
        """Test du filtre par plage de montants."""
        min_amt = 1000
        max_amt = 5000
        response = self.client.get(
            f"/api/transactions?min_amount={min_amt}&max_amount={max_amt}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Toutes les transactions doivent être dans la plage
        for transaction in data["transactions"]:
            self.assertGreaterEqual(transaction["amount"], min_amt)
            self.assertLessEqual(transaction["amount"], max_amt)

    def test_search_endpoint_combines_filters(self) -> None:
        """Test que la recherche combine plusieurs filtres."""
        search_data = {"use_chip": "Chip Transaction", "amount_range": [10, 100]}
        response = self.client.post("/api/transactions/search", json=search_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Vérifier que tous les critères sont respectés
        for transaction in data["transactions"]:
            self.assertEqual(transaction["use_chip"], "Chip Transaction")
            self.assertGreaterEqual(transaction["amount"], 10)
            self.assertLessEqual(transaction["amount"], 100)

    def test_customer_transactions_consistency(self) -> None:
        """Test la cohérence des transactions par client."""
        # Récupérer un client
        list_response = self.client.get("/api/transactions?limit=1")
        transactions = list_response.json()["transactions"]

        if transactions:
            customer_id = transactions[0]["client_id"]

            # Récupérer toutes ses transactions
            response = self.client.get(f"/api/transactions/by-customer/{customer_id}")
            self.assertEqual(response.status_code, 200)
            customer_transactions = response.json()

            # Toutes doivent avoir ce client comme origine
            for transaction in customer_transactions:
                self.assertEqual(transaction["client_id"], customer_id)


if __name__ == "__main__":
    unittest.main()
