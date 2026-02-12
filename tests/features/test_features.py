"""
Feature tests using unittest.

This module provides feature-level tests for the Banking Transactions API.
"""

import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


class TestTransactionsFeature(unittest.TestCase):
    """Feature tests for transaction operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_data = [
            {
                "id": "tx_0000001",
                "step": 1,
                "type": "PAYMENT",
                "amount": 100.0,
                "nameOrig": "C001",
                "oldbalanceOrg": 1000.0,
                "newbalanceOrig": 900.0,
                "nameDest": "M001",
                "oldbalanceDest": 0.0,
                "newbalanceDest": 0.0,
                "isFraud": 0,
                "isFlaggedFraud": 0,
            },
        ]
        
        from app.services import transactions_service
        self.patcher = patch.object(transactions_service, '_get_data', return_value=self.mock_data)
        self.patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()

    def test_complete_transaction_workflow(self):
        """Test complete transaction workflow."""
        # List transactions
        response = self.client.get("/api/transactions")
        self.assertEqual(response.status_code, 200)
        
        # Vérifiez la structure de la réponse
        data = response.json()
        self.assertIn("transactions", data)
        self.assertIn("total", data)
        self.assertIn("page", data)


class TestStatisticsFeature(unittest.TestCase):
    """Feature tests for statistics operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_data = [
            {
                "step": 1,
                "type": "PAYMENT",
                "amount": 100.0,
                "nameOrig": "C001",
                "oldbalanceOrg": 1000.0,
                "newbalanceOrig": 900.0,
                "nameDest": "M001",
                "oldbalanceDest": 0.0,
                "newbalanceDest": 0.0,
                "isFraud": 0,
                "isFlaggedFraud": 0,
            },
        ]
        
        from app.services import stats_service
        self.patcher = patch.object(stats_service, '_get_data', return_value=self.mock_data)
        self.patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()

    def test_statistics_aggregation(self):
        """Test statistics aggregation."""
        response = self.client.get("/api/stats/overview")
        self.assertEqual(response.status_code, 200)


class TestFraudDetectionFeature(unittest.TestCase):
    """Feature tests for fraud detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_fraud_prediction(self):
        """Test fraud prediction."""
        response = self.client.post(
            "/api/fraud/predict",
            json={
                "type": "TRANSFER",
                "amount": 500000.0,
                "oldbalanceOrg": 600000.0,
                "newbalanceOrig": 0.0,
            }
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()