"""
Feature tests for all 20 API routes using unittest + TestClient.

Each test verifies the HTTP status code and basic shape of the response
for the corresponding endpoint.
"""

import unittest
import pandas as pd
from fastapi.testclient import TestClient

from banking_api.main import app
from banking_api.services.data_loader import DataLoader

FIXTURE_DATA = {
    "id": ["tx_0000001", "tx_0000002", "tx_0000003", "tx_0000004", "tx_0000005"],
    "step": [1, 1, 2, 2, 3],
    "type": ["TRANSFER", "CASH_OUT", "PAYMENT", "TRANSFER", "CASH_OUT"],
    "amount": [1000.0, 500.0, 200.0, 8000.0, 300.0],
    "nameOrig": ["C001", "C002", "C001", "C003", "C002"],
    "oldbalanceOrg": [5000.0, 1000.0, 300.0, 9000.0, 800.0],
    "newbalanceOrig": [4000.0, 500.0, 100.0, 1000.0, 500.0],
    "nameDest": ["C010", "C011", "C012", "C013", "C014"],
    "oldbalanceDest": [0.0, 0.0, 0.0, 0.0, 0.0],
    "newbalanceDest": [1000.0, 500.0, 200.0, 8000.0, 300.0],
    "isFraud": [0, 0, 0, 1, 0],
    "isFlaggedFraud": [0, 0, 0, 1, 0],
}


def _inject_fixture() -> None:
    """Inject fixture data into the DataLoader singleton."""
    DataLoader.reset()
    loader = DataLoader.__new__(DataLoader)
    loader._df = pd.DataFrame(FIXTURE_DATA)
    loader._deleted_ids = set()
    DataLoader._instance = loader


class TestTransactionRoutes(unittest.TestCase):
    """Tests for routes 1–8 (Transactions)."""

    def setUp(self) -> None:
        _inject_fixture()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        DataLoader.reset()

    # Route 1
    def test_list_transactions(self) -> None:
        response = self.client.get("/api/transactions?page=1&limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("transactions", data)
        self.assertIn("total", data)

    # Route 2
    def test_get_transaction_by_id(self) -> None:
        response = self.client.get("/api/transactions/tx_0000001")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], "tx_0000001")

    # Route 2 — not found
    def test_get_transaction_not_found(self) -> None:
        response = self.client.get("/api/transactions/tx_9999999")
        self.assertEqual(response.status_code, 404)

    # Route 3
    def test_search_transactions(self) -> None:
        response = self.client.post(
            "/api/transactions/search",
            json={"type": "TRANSFER", "isFraud": 0},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    # Route 4
    def test_get_types(self) -> None:
        response = self.client.get("/api/transactions/types")
        self.assertEqual(response.status_code, 200)
        self.assertIn("TRANSFER", response.json())

    # Route 5
    def test_get_recent(self) -> None:
        response = self.client.get("/api/transactions/recent?n=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    # Route 6
    def test_delete_transaction(self) -> None:
        response = self.client.delete("/api/transactions/tx_0000001")
        self.assertEqual(response.status_code, 200)
        self.assertIn("deleted", response.json()["message"].lower())

    # Route 6 — not found
    def test_delete_not_found(self) -> None:
        response = self.client.delete("/api/transactions/tx_9999999")
        self.assertEqual(response.status_code, 404)

    # Route 7
    def test_by_customer(self) -> None:
        response = self.client.get("/api/transactions/by-customer/C001")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(all(t["nameOrig"] == "C001" for t in data))

    # Route 8
    def test_to_customer(self) -> None:
        response = self.client.get("/api/transactions/to-customer/C010")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(all(t["nameDest"] == "C010" for t in data))


class TestStatsRoutes(unittest.TestCase):
    """Tests for routes 9–12 (Statistics)."""

    def setUp(self) -> None:
        _inject_fixture()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        DataLoader.reset()

    # Route 9
    def test_overview(self) -> None:
        response = self.client.get("/api/stats/overview")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_transactions", data)
        self.assertIn("fraud_rate", data)

    # Route 10
    def test_amount_distribution(self) -> None:
        response = self.client.get("/api/stats/amount-distribution")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("bins", data)
        self.assertIn("counts", data)

    # Route 11
    def test_by_type(self) -> None:
        response = self.client.get("/api/stats/by-type")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    # Route 12
    def test_daily(self) -> None:
        response = self.client.get("/api/stats/daily")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


class TestFraudRoutes(unittest.TestCase):
    """Tests for routes 13–15 (Fraud)."""

    def setUp(self) -> None:
        _inject_fixture()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        DataLoader.reset()

    # Route 13
    def test_fraud_summary(self) -> None:
        response = self.client.get("/api/fraud/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_frauds", data)

    # Route 14
    def test_fraud_by_type(self) -> None:
        response = self.client.get("/api/fraud/by-type")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    # Route 15
    def test_fraud_predict(self) -> None:
        response = self.client.post(
            "/api/fraud/predict",
            json={
                "type": "TRANSFER",
                "amount": 500000.0,
                "oldbalanceOrg": 500000.0,
                "newbalanceOrig": 0.0,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("isFraud", data)
        self.assertIn("probability", data)


class TestCustomerRoutes(unittest.TestCase):
    """Tests for routes 16–18 (Customers)."""

    def setUp(self) -> None:
        _inject_fixture()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        DataLoader.reset()

    # Route 16
    def test_list_customers(self) -> None:
        response = self.client.get("/api/customers?page=1&limit=10")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    # Route 17
    def test_customer_profile(self) -> None:
        response = self.client.get("/api/customers/C001")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], "C001")

    # Route 17 — not found
    def test_customer_not_found(self) -> None:
        response = self.client.get("/api/customers/UNKNOWN")
        self.assertEqual(response.status_code, 404)

    # Route 18
    def test_top_customers(self) -> None:
        response = self.client.get("/api/customers/top?n=3")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLessEqual(len(data), 3)


class TestSystemRoutes(unittest.TestCase):
    """Tests for routes 19–20 (Administration)."""

    def setUp(self) -> None:
        _inject_fixture()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        DataLoader.reset()

    # Route 19
    def test_health(self) -> None:
        response = self.client.get("/api/system/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("uptime", data)

    # Route 20
    def test_metadata(self) -> None:
        response = self.client.get("/api/system/metadata")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("version", data)
        self.assertIn("last_update", data)


if __name__ == "__main__":
    unittest.main()
