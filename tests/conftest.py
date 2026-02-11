"""Pytest configuration and fixtures.

This module provides shared fixtures for testing.
"""

import pytest
import pandas as pd
from fastapi.testclient import TestClient
from banking_api.app import create_app
from banking_api.utils.data_loader import DataLoader


@pytest.fixture(scope="session")
def sample_data() -> pd.DataFrame:
    """Create sample transaction data for testing.

    Returns
    -------
    pd.DataFrame
        Sample transaction data matching Kaggle dataset format.
    """
    data = {
        'id': ['tx_0000000', 'tx_0000001', 'tx_0000002', 'tx_0000003', 'tx_0000004'],
        'date': ['2010-01-01 00:01:00', '2010-01-01 00:02:00', '2010-01-01 00:03:00',
                 '2010-01-01 00:04:00', '2010-01-01 00:05:00'],
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
    return pd.DataFrame(data)


@pytest.fixture(scope="session")
def load_sample_data(sample_data: pd.DataFrame) -> None:
    """Load sample data into DataLoader.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample transaction data.
    """
    loader = DataLoader()
    loader._data = sample_data


@pytest.fixture
def client(load_sample_data: None) -> TestClient:
    """Create test client.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.

    Returns
    -------
    TestClient
        FastAPI test client.
    """
    app = create_app()
    return TestClient(app)
