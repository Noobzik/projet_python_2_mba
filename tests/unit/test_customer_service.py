"""
Tests unitaires pour le service client.
"""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from banking_api.models.schemas import CustomerListResponse
from banking_api.services.customer_service import CustomerService


class TestCustomerService(unittest.TestCase):
    """Tests pour le service client."""

    def setUp(self) -> None:
        """Configuration initiale des tests."""
        self.mock_data_loader = MagicMock()

        # Créer un DataFrame de test
        data = {
            "client_id": [1, 1, 2, 3, 2],
            "amount": [100.0, 50.0, 200.0, 300.0, 20.0],
            "errors": [None, "Error", None, None, None],
            "merchant_state": ["CA", "NY", "CA", "TX", "CA"],
            "use_chip": [
                "Chip Transaction",
                "Online Transaction",
                "Chip Transaction",
                "Swipe Transaction",
                "Chip Transaction",
            ],
            "card_id": [101, 101, 102, 103, 102],
            "merchant_id": [1001, 1002, 1001, 1003, 1001],
            "date": [
                "2023-01-01",
                "2023-01-02",
                "2023-01-03",
                "2023-01-04",
                "2023-01-05",
            ],
        }
        self.test_df = pd.DataFrame(data)

        # Patcher le data_loader dans le service
        self.patcher = patch(
            "banking_api.services.customer_service.data_loader", self.mock_data_loader
        )
        self.patcher.start()

        self.customer_service = CustomerService()
        self.mock_data_loader.get_transactions.return_value = self.test_df

    def tearDown(self) -> None:
        """Nettoyage après les tests."""
        self.patcher.stop()

    def test_get_all_customers(self) -> None:
        """Test de récupération de tous les clients."""
        response = self.customer_service.get_all_customers(page=1, limit=10)

        self.assertIsInstance(response, CustomerListResponse)
        self.assertEqual(response.total, 3)  # Clients 1, 2, 3
        self.assertEqual(response.customers, [1, 2, 3])

    def test_get_customer_profile(self) -> None:
        """Test de récupération du profil client."""
        # Client 1: 2 transactions, total 150, 1 erreur
        profile = self.customer_service.get_customer_profile(1)

        self.assertIsNotNone(profile)
        if profile:
            self.assertEqual(profile.id, 1)
            self.assertEqual(profile.transactions_count, 2)
            self.assertEqual(profile.total_amount, 150.0)
            self.assertTrue(profile.fraudulent)

    def test_get_customer_profile_not_found(self) -> None:
        """Test avec un client inexistant."""
        profile = self.customer_service.get_customer_profile(999)
        self.assertIsNone(profile)

    def test_get_top_customers_by_volume(self) -> None:
        """Test des meilleurs clients par volume."""
        top_customers = self.customer_service.get_top_customers(n=2, by="volume")

        self.assertEqual(len(top_customers), 2)
        # Client 3: 300, Client 2: 220, Client 1: 150
        self.assertEqual(top_customers[0].id, 3)
        self.assertEqual(top_customers[1].id, 2)

    def test_get_top_customers_by_count(self) -> None:
        """Test des meilleurs clients par nombre de transactions."""
        top_customers = self.customer_service.get_top_customers(n=2, by="count")

        self.assertEqual(len(top_customers), 2)
        # Client 1: 2, Client 2: 2, Client 3: 1
        # L'ordre entre 1 et 2 peut varier car égalité, mais ce sont les deux premiers
        ids = [c.id for c in top_customers]
        self.assertIn(1, ids)
        self.assertIn(2, ids)

    def test_get_customer_transaction_history(self) -> None:
        """Test de l'historique des transactions."""
        history = self.customer_service.get_customer_transaction_history(1)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["client_id"], 1)

    def test_get_customer_statistics(self) -> None:
        """Test des statistiques détaillées du client."""
        stats = self.customer_service.get_customer_statistics(1)

        self.assertEqual(stats["customer_id"], 1)
        self.assertEqual(stats["total_transactions"], 2)
        self.assertEqual(stats["total_amount"], 150.0)
        self.assertTrue(stats["fraud_involved"])
        self.assertEqual(stats["unique_cards"], 1)

    def test_get_customer_statistics_not_found(self) -> None:
        """Test des statistiques pour un client inexistant."""
        stats = self.customer_service.get_customer_statistics(999)
        self.assertEqual(stats, {})
