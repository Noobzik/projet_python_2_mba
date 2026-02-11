"""Feature tests using unittest.

This module provides integration tests for API features.
"""

import unittest
from fastapi.testclient import TestClient
import pandas as pd
from banking_api.app import create_app
from banking_api.utils.data_loader import DataLoader


class TestAPIFeatures(unittest.TestCase):
    """Test suite for API feature integration tests."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures for the entire test class.

        This method runs once before all tests.
        """
        data = {
            'id': [
                'tx_0000000', 'tx_0000001', 'tx_0000002',
                'tx_0000003', 'tx_0000004'
            ],
            'date': [
                '2010-01-01 00:01:00', '2010-01-01 00:02:00',
                '2010-01-01 00:03:00', '2010-01-01 00:04:00',
                '2010-01-01 00:05:00'
            ],
            'client_id': [1556, 1557, 1558, 1556, 1557],
            'card_id': [2972, 2973, 2974, 2972, 2973],
            'amount': [77.00, 181.0, 181.0, 1000.0, 5000.0],
            'use_chip': ['Swipe Transaction', 'Chip Transaction', 'Online Transaction',
                         'Swipe Transaction', 'Chip Transaction'],
            'merchant_id': [59935, 59936, 59937, 59935, 59936],
            'merchant_city': ['Beulah', 'Fargo', 'Bismarck', 'Beulah', 'Fargo'],
            'merchant_state': ['ND', 'ND', 'ND', 'ND', 'ND'],
            'zip': [58523.0, 58102.0, 58501.0, 58523.0, 58102.0],
            'mcc': [5499, 5812, 5411, 5499, 5812],
            'errors': ['', '', '', '', ''],
            'isFraud': [0, 1, 1, 0, 0]
        }
        df = pd.DataFrame(data)

        loader = DataLoader()
        loader._data = df

        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def test_transaction_workflow(self) -> None:
        """Test complete transaction workflow.

        This test verifies:
        1. Listing transactions
        2. Getting specific transaction
        3. Searching transactions
        4. Filtering transactions
        """
        response = self.client.get("/api/transactions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("transactions", data)

        if len(data["transactions"]) > 0:
            tx_id = data["transactions"][0]["id"]
            response = self.client.get(f"/api/transactions/{tx_id}")
            self.assertEqual(response.status_code, 200)

        search_criteria = {"use_chip": "Swipe"}
        response = self.client.post("/api/transactions/search", json=search_criteria)
        self.assertEqual(response.status_code, 200)

    def test_statistics_workflow(self) -> None:
        """Test complete statistics workflow.

        This test verifies:
        1. Getting overview statistics
        2. Getting amount distribution
        3. Getting stats by type
        4. Getting daily stats
        """
        response = self.client.get("/api/stats/overview")
        self.assertEqual(response.status_code, 200)
        overview = response.json()
        self.assertGreater(overview["total_transactions"], 0)

        response = self.client.get("/api/stats/amount-distribution")
        self.assertEqual(response.status_code, 200)
        distribution = response.json()
        self.assertIn("bins", distribution)

        response = self.client.get("/api/stats/by-type")
        self.assertEqual(response.status_code, 200)
        stats = response.json()
        self.assertIsInstance(stats, list)

        response = self.client.get("/api/stats/daily")
        self.assertEqual(response.status_code, 200)

    def test_fraud_detection_workflow(self) -> None:
        """Test complete fraud detection workflow.

        This test verifies:
        1. Getting fraud summary
        2. Getting fraud by type
        3. Predicting fraud for new transaction
        """
        response = self.client.get("/api/fraud/summary")
        self.assertEqual(response.status_code, 200)
        summary = response.json()
        self.assertIn("total_frauds", summary)

        response = self.client.get("/api/fraud/by-type")
        self.assertEqual(response.status_code, 200)
        fraud_stats = response.json()
        self.assertIsInstance(fraud_stats, list)

        transaction = {
            "amount": 300000.0,
            "use_chip": "Online Transaction",
            "merchant_state": "CA",
            "mcc": 5999
        }
        response = self.client.post("/api/fraud/predict", json=transaction)
        self.assertEqual(response.status_code, 200)
        prediction = response.json()
        self.assertIn("isFraud", prediction)
        self.assertIn("probability", prediction)

    def test_customer_workflow(self) -> None:
        """Test complete customer workflow.

        This test verifies:
        1. Listing customers
        2. Getting customer profile
        3. Getting top customers
        """
        response = self.client.get("/api/customers")
        self.assertEqual(response.status_code, 200)
        customers = response.json()
        self.assertIn("customers", customers)

        if len(customers["customers"]) > 0:
            customer_id = customers["customers"][0]
            response = self.client.get(f"/api/customers/{customer_id}")
            self.assertEqual(response.status_code, 200)
            profile = response.json()
            self.assertEqual(profile["id"], customer_id)

        response = self.client.get("/api/customers/top?n=5")
        self.assertEqual(response.status_code, 200)
        top_customers = response.json()
        self.assertIsInstance(top_customers, list)

    def test_system_monitoring_workflow(self) -> None:
        """Test system monitoring workflow.

        This test verifies:
        1. Health check
        2. Metadata retrieval
        """
        response = self.client.get("/api/system/health")
        self.assertEqual(response.status_code, 200)
        health = response.json()
        self.assertIn("status", health)
        self.assertIn(health["status"], ["ok", "degraded", "error"])

        response = self.client.get("/api/system/metadata")
        self.assertEqual(response.status_code, 200)
        metadata = response.json()
        self.assertEqual(metadata["version"], "1.0.0")

    def test_pagination_feature(self) -> None:
        """Test pagination across multiple endpoints.

        This test verifies pagination works consistently.
        """
        response = self.client.get("/api/transactions?page=1&limit=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["limit"], 2)

        response = self.client.get("/api/customers?page=1&limit=1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["page"], 1)

    def test_filtering_feature(self) -> None:
        """Test filtering capabilities.

        This test verifies filtering works across endpoints.
        """
        response = self.client.get("/api/transactions?use_chip=Swipe&isFraud=0")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for tx in data["transactions"]:
            self.assertIn("Swipe", tx["use_chip"])
            self.assertEqual(tx["isFraud"], 0)

    def test_error_handling_feature(self) -> None:
        """Test error handling across endpoints.

        This test verifies proper error responses.
        """
        response = self.client.get("/api/transactions/invalid_id")
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/api/customers/99999")
        self.assertEqual(response.status_code, 404)

        response = self.client.delete("/api/transactions/invalid_id")
        self.assertEqual(response.status_code, 404)

    def test_data_consistency_feature(self) -> None:
        """Test data consistency across endpoints.

        This test verifies data is consistent when accessed
        through different endpoints.
        """
        response = self.client.get("/api/stats/overview")
        self.assertEqual(response.status_code, 200)
        overview = response.json()

        response = self.client.get("/api/transactions?limit=100")
        self.assertEqual(response.status_code, 200)
        transactions = response.json()

        self.assertEqual(overview["total_transactions"], transactions["total"])


if __name__ == '__main__':
    unittest.main()
