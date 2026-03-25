"""
Pytest configuration and shared fixtures.

A small in-memory DataFrame is injected into every test so that the
real CSV file is never required during the test suite.
"""

import pandas as pd
import pytest

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


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Return a small fixture DataFrame with 5 transactions."""
    return pd.DataFrame(FIXTURE_DATA)


@pytest.fixture(autouse=True)
def reset_data_loader():
    """Reset the DataLoader singleton before each test."""
    DataLoader.reset()
    yield
    DataLoader.reset()
