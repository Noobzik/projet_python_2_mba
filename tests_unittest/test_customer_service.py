"""Tests unittest pour le service de gestion des clients."""
import unittest
import os
import tempfile
import pandas as pd
from unittest.mock import patch
from fastapi import HTTPException
from banking_api.services import customer_service


class TestCustomerService(unittest.TestCase):
    """Tests pour le service clients."""

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
        self.patcher = patch.object(customer_service, '_get_csv_path', return_value=self.csv_path)
        self.patcher.start()

    def tearDown(self):
        """Nettoyage après chaque test."""
        self.patcher.stop()

    def test_get_customers(self):
        """Test de récupération de la liste des clients."""
        result = customer_service.get_customers(page=1, limit=10)

        self.assertIn('page', result)
        self.assertIn('limit', result)
        self.assertIn('total', result)
        self.assertIn('customers', result)

        self.assertEqual(result['page'], 1)
        self.assertEqual(result['limit'], 10)
        self.assertEqual(result['total'], 4)

    def test_get_customers_pagination(self):
        """Test de la pagination."""
        result = customer_service.get_customers(page=1, limit=2)

        self.assertEqual(len(result['customers']), 2)
        self.assertEqual(result['total'], 4)

    def test_get_customer_profile(self):
        """Test du profil client."""
        profile = customer_service.get_customer_profile('C1231006815')

        self.assertIn('id', profile)
        self.assertIn('transactions_count', profile)
        self.assertIn('avg_amount', profile)
        self.assertIn('total_amount', profile)
        self.assertIn('fraudulent', profile)
        self.assertIn('fraud_count', profile)

        self.assertEqual(profile['id'], 'C1231006815')
        self.assertEqual(profile['transactions_count'], 2)
        self.assertGreater(profile['avg_amount'], 0)
        self.assertGreater(profile['total_amount'], 0)

    def test_get_customer_profile_fraudulent(self):
        """Test de profil pour client avec fraude."""
        profile = customer_service.get_customer_profile('C1666544295')

        self.assertEqual(profile['fraudulent'], True)
        self.assertEqual(profile['fraud_count'], 1)

    def test_get_customer_profile_not_fraudulent(self):
        """Test de profil pour client sans fraude."""
        profile = customer_service.get_customer_profile('C1231006815')

        self.assertEqual(profile['fraudulent'], False)
        self.assertEqual(profile['fraud_count'], 0)

    def test_get_customer_profile_not_found(self):
        """Test de profil inexistant."""
        with self.assertRaises(HTTPException) as context:
            customer_service.get_customer_profile('C9999999999')

        self.assertEqual(context.exception.status_code, 404)

    def test_get_top_customers_by_volume(self):
        """Test du top clients par volume."""
        top = customer_service.get_top_customers(n=3, by='volume')

        self.assertIsInstance(top, list)
        self.assertLessEqual(len(top), 3)

        for customer in top:
            self.assertIn('customer_id', customer)
            self.assertIn('transaction_count', customer)
            self.assertIn('total_amount', customer)
            self.assertIn('avg_amount', customer)
            self.assertIn('fraud_count', customer)
            self.assertIn('fraudulent', customer)

    def test_get_top_customers_by_count(self):
        """Test du top clients par nombre."""
        top = customer_service.get_top_customers(n=3, by='count')

        self.assertIsInstance(top, list)
        self.assertLessEqual(len(top), 3)

    def test_get_top_customers_sorted(self):
        """Test du tri des top clients."""
        top = customer_service.get_top_customers(n=10, by='volume')

        amounts = [c['total_amount'] for c in top]
        self.assertEqual(amounts, sorted(amounts, reverse=True))


if __name__ == '__main__':
    unittest.main()
