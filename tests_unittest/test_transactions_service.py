"""Tests unittest pour le service de gestion des transactions."""
import unittest
import os
import tempfile
import pandas as pd
from unittest.mock import patch
from fastapi import HTTPException
from banking_api.services import transactions_service


class TestTransactionsService(unittest.TestCase):
    """Tests pour le service de transactions."""

    @classmethod
    def setUpClass(cls):
        """Configuration avant tous les tests."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.csv_path = os.path.join(cls.temp_dir, 'transactions_data.csv')

        # Créer données de test
        data = {
            'step': [1, 1, 2, 2, 3],
            'type': ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT', 'PAYMENT'],
            'amount': [9839.64, 181.00, 181.00, 52.95, 1234.56],
            'nameOrig': ['C1231006815', 'C1666544295', 'C1305486145', 'C840083671', 'C1231006815'],
            'oldbalanceOrg': [170136.00, 181.00, 181.00, 41720.00, 168902.36],
            'newbalanceOrig': [160296.36, 0.00, 0.00, 41667.05, 167667.80],
            'nameDest': ['M1979787155', 'C1900366749', 'C840083671', 'C1634788479', 'M1234567890'],
            'oldbalanceDest': [0.00, 0.00, 21182.00, 41898.00, 0.00],
            'newbalanceDest': [0.00, 0.00, 21182.00, 41950.95, 0.00],
            'isFraud': [0, 1, 0, 0, 0],
            'isFlaggedFraud': [0, 0, 0, 0, 0]
        }
        df = pd.DataFrame(data)
        df.to_csv(cls.csv_path, index=False)

    def setUp(self):
        """Configuration avant chaque test."""
        self.patcher = patch.object(
            transactions_service,
            '_get_csv_path',
            return_value=self.csv_path)
        self.patcher.start()

    def tearDown(self):
        """Nettoyage après chaque test."""
        self.patcher.stop()

    def test_get_paginated_transactions(self):
        """Test de pagination des transactions."""
        result = transactions_service.get_paginated_transactions(page=1, limit=2)

        self.assertEqual(result['page'], 1)
        self.assertEqual(result['limit'], 2)
        self.assertEqual(result['total'], 5)
        self.assertEqual(len(result['transactions']), 2)

    def test_get_paginated_transactions_with_type_filter(self):
        """Test avec filtre de type."""
        result = transactions_service.get_paginated_transactions(
            page=1, limit=10, type_filter='PAYMENT'
        )

        self.assertEqual(result['total'], 2)
        for transaction in result['transactions']:
            self.assertEqual(transaction['type'], 'PAYMENT')

    def test_get_paginated_transactions_with_fraud_filter(self):
        """Test avec filtre de fraude."""
        result = transactions_service.get_paginated_transactions(
            page=1, limit=10, is_fraud=1
        )

        self.assertEqual(result['total'], 1)
        for transaction in result['transactions']:
            self.assertEqual(transaction['isFraud'], 1)

    def test_get_paginated_transactions_with_amount_range(self):
        """Test avec filtre de montant."""
        result = transactions_service.get_paginated_transactions(
            page=1, limit=10, min_amount=100, max_amount=200
        )

        self.assertEqual(result['total'], 2)
        for transaction in result['transactions']:
            self.assertGreaterEqual(transaction['amount'], 100)
            self.assertLessEqual(transaction['amount'], 200)

    def test_get_transaction_by_id(self):
        """Test de récupération par ID."""
        transaction = transactions_service.get_transaction_by_id('0')

        self.assertIsNotNone(transaction)
        self.assertEqual(transaction['type'], 'PAYMENT')
        self.assertEqual(transaction['amount'], 9839.64)

    def test_get_transaction_by_id_not_found(self):
        """Test avec ID inexistant."""
        transaction = transactions_service.get_transaction_by_id('999')

        self.assertIsNone(transaction)

    def test_get_transaction_by_id_invalid(self):
        """Test avec ID invalide."""
        transaction = transactions_service.get_transaction_by_id('abc')

        self.assertIsNone(transaction)

    def test_get_transaction_types(self):
        """Test de récupération des types."""
        types = transactions_service.get_transaction_types()

        self.assertIsInstance(types, list)
        self.assertEqual(len(types), 4)
        self.assertIn('PAYMENT', types)
        self.assertIn('TRANSFER', types)

    def test_get_recent_transactions(self):
        """Test des transactions récentes."""
        recent = transactions_service.get_recent_transactions(n=3)

        self.assertEqual(len(recent), 3)

    def test_search_transactions_by_type(self):
        """Test de recherche par type."""
        results = transactions_service.search_transactions(type_filter='PAYMENT')

        self.assertEqual(len(results), 2)
        for transaction in results:
            self.assertEqual(transaction['type'], 'PAYMENT')

    def test_search_transactions_by_fraud(self):
        """Test de recherche par fraude."""
        results = transactions_service.search_transactions(is_fraud=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['isFraud'], 1)

    def test_get_transactions_by_customer(self):
        """Test par client."""
        transactions = transactions_service.get_transactions_by_customer('C1231006815')

        self.assertEqual(len(transactions), 2)
        for transaction in transactions:
            self.assertEqual(transaction['nameOrig'], 'C1231006815')

    def test_get_transactions_to_customer(self):
        """Test des transactions reçues."""
        transactions = transactions_service.get_transactions_to_customer('C840083671')

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['nameDest'], 'C840083671')

    def test_delete_transaction(self):
        """Test de suppression."""
        result = transactions_service.delete_transaction('0')

        self.assertIn('message', result)
        self.assertIn('0', result['message'])

    def test_missing_csv_file(self):
        """Test avec fichier CSV manquant."""
        with patch.object(
            transactions_service,
            '_get_csv_path',
            return_value='/nonexistent/file.csv'
        ):
            with self.assertRaises(HTTPException) as context:
                transactions_service.get_paginated_transactions(
                    page=1, limit=10)

            self.assertEqual(context.exception.status_code, 404)


if __name__ == '__main__':
    unittest.main()
