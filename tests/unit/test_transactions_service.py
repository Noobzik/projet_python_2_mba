"""
Tests unitaires pour le service de transactions.
"""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from banking_api.models.schemas import TransactionResponse, TransactionSearch
from banking_api.services.transactions_service import TransactionsService


class TestTransactionsService(unittest.TestCase):
    """Tests pour le service de transactions."""

    def setUp(self) -> None:
        """Configuration initiale des tests."""
        self.mock_data_loader = MagicMock()

        # Créer un DataFrame de test
        data = {
            "id": [1, 2, 3, 4, 5],
            "amount": [100.0, 50.0, 200.0, 300.0, 20.0],
            "use_chip": [
                "Chip Transaction",
                "Online Transaction",
                "Chip Transaction",
                "Swipe Transaction",
                "Chip Transaction",
            ],
            "merchant_state": ["CA", "NY", "CA", "TX", "CA"],
            "errors": [None, "Error", None, None, None],
            "client_id": [1, 1, 2, 3, 2],
            "card_id": [101, 101, 102, 103, 102],
            "merchant_id": [1001, 1002, 1001, 1003, 1001],
            "mcc": [5000, 5001, 5000, 5002, 5000],
            "date": [
                "2023-01-01",
                "2023-01-02",
                "2023-01-03",
                "2023-01-04",
                "2023-01-05",
            ],
            "merchant_city": ["City1", "City2", "City1", "City3", "City1"],
            "zip": [90001, 10001, 90001, 75001, 90001],
        }
        self.test_df = pd.DataFrame(data)

        # Patcher le data_loader dans le service
        self.patcher = patch(
            "banking_api.services.transactions_service.data_loader",
            self.mock_data_loader,
        )
        self.patcher.start()

        self.transactions_service = TransactionsService()
        self.mock_data_loader.get_transactions.return_value = self.test_df

    def tearDown(self) -> None:
        """Nettoyage après les tests."""
        self.patcher.stop()

    def test_get_all_transactions(self) -> None:
        """Test de récupération de toutes les transactions."""
        response = self.transactions_service.get_all_transactions(page=1, limit=10)

        self.assertIsInstance(response, TransactionResponse)
        self.assertEqual(response.total, 5)
        self.assertEqual(len(response.transactions), 5)

    def test_get_all_transactions_with_filters(self) -> None:
        """Test de récupération avec filtres."""
        # Filtre par use_chip
        response = self.transactions_service.get_all_transactions(
            use_chip="Chip Transaction"
        )
        self.assertEqual(response.total, 3)

        # Filtre par merchant_state
        response = self.transactions_service.get_all_transactions(merchant_state="NY")
        self.assertEqual(response.total, 1)

        # Filtre par has_errors (True)
        response = self.transactions_service.get_all_transactions(has_errors=True)
        self.assertEqual(response.total, 1)

        # Filtre par has_errors (False)
        response = self.transactions_service.get_all_transactions(has_errors=False)
        self.assertEqual(response.total, 4)

        # Filtre par min_amount
        response = self.transactions_service.get_all_transactions(min_amount=150.0)
        self.assertEqual(response.total, 2)  # 200 et 300

        # Filtre par max_amount
        response = self.transactions_service.get_all_transactions(max_amount=60.0)
        self.assertEqual(response.total, 2)  # 50 et 20

    def test_get_transaction_by_id(self) -> None:
        """Test de récupération par ID."""
        transaction = self.transactions_service.get_transaction_by_id(1)
        self.assertIsNotNone(transaction)
        if transaction:
            self.assertEqual(transaction.id, 1)
            self.assertEqual(transaction.amount, 100.0)

    def test_get_transaction_by_id_not_found(self) -> None:
        """Test de récupération par ID inexistant."""
        transaction = self.transactions_service.get_transaction_by_id(999)
        self.assertIsNone(transaction)

    def test_search_transactions(self) -> None:
        """Test de recherche de transactions."""
        criteria = TransactionSearch(client_id=1, amount_range=[40.0, 110.0])
        response = self.transactions_service.search_transactions(criteria)

        self.assertEqual(response.total, 2)  # ID 1 (100.0) et ID 2 (50.0)

        # Test avec isFraud
        criteria_fraud = TransactionSearch(isFraud=True)
        response = self.transactions_service.search_transactions(criteria_fraud)
        self.assertEqual(response.total, 1)  # ID 2

        # Test avec merchant_id
        criteria_merchant = TransactionSearch(merchant_id=1001)
        response = self.transactions_service.search_transactions(criteria_merchant)
        self.assertEqual(response.total, 3)  # ID 1, 3, 5

    def test_get_transaction_types(self) -> None:
        """Test de récupération des types de transactions."""
        types = self.transactions_service.get_transaction_types()
        self.assertIsInstance(types, list)
        self.assertIn("Chip Transaction", types)
        self.assertIn("Online Transaction", types)
        self.assertIn("Swipe Transaction", types)

    def test_get_recent_transactions(self) -> None:
        """Test de récupération des transactions récentes."""
        recent = self.transactions_service.get_recent_transactions(n=2)
        self.assertEqual(len(recent), 2)
        # Les 2 dernières sont ID 4 et 5
        ids = [t.id for t in recent]
        self.assertIn(4, ids)
        self.assertIn(5, ids)

    def test_delete_transaction(self) -> None:
        """Test de suppression de transaction."""
        # Supprimer ID 1
        success = self.transactions_service.delete_transaction(1)
        self.assertTrue(success)

        # Vérifier que le DataFrame a été mis à jour dans le mock (en fait, dans l'attribut _transactions_df du mock)
        # Comme on a assigné self.test_df au retour de get_transactions, on doit vérifier si _transactions_df a été mis à jour
        # Mais dans le code, on fait self.data_loader._transactions_df = filtered_df
        # Donc on doit vérifier self.mock_data_loader._transactions_df

        # Note: le mock est un MagicMock, donc l'assignation d'attribut fonctionne
        self.assertIsNotNone(self.mock_data_loader._transactions_df)
        if self.mock_data_loader._transactions_df is not None:
            self.assertEqual(len(self.mock_data_loader._transactions_df), 4)

    def test_delete_transaction_not_found(self) -> None:
        """Test de suppression d'une transaction inexistante."""
        success = self.transactions_service.delete_transaction(999)
        self.assertFalse(success)

    def test_get_transactions_by_customer(self) -> None:
        """Test de récupération des transactions par client."""
        transactions = self.transactions_service.get_transactions_by_customer(1)
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].client_id, 1)
