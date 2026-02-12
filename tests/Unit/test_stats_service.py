"""
Unit tests for statistics service.

This module tests statistical analysis functions.
"""

import pytest
from unittest.mock import patch
from app.services import stats_service


@pytest.fixture
def mock_transactions():
    """Mock transaction data for testing."""
    return [
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
        {
            "step": 1,
            "type": "TRANSFER",
            "amount": 5000.0,
            "nameOrig": "C002",
            "oldbalanceOrg": 10000.0,
            "newbalanceOrig": 5000.0,
            "nameDest": "C003",
            "oldbalanceDest": 0.0,
            "newbalanceDest": 5000.0,
            "isFraud": 1,
            "isFlaggedFraud": 0,
        },
        {
            "step": 2,
            "type": "PAYMENT",
            "amount": 50.0,
            "nameOrig": "C003",
            "oldbalanceOrg": 200.0,
            "newbalanceOrig": 150.0,
            "nameDest": "M001",
            "oldbalanceDest": 0.0,
            "newbalanceDest": 0.0,
            "isFraud": 0,
            "isFlaggedFraud": 0,
        },
    ]


@pytest.fixture(autouse=True)
def setup_mock_data(mock_transactions):
    """Setup mock data before each test."""
    with patch.object(stats_service, '_get_data', return_value=mock_transactions):
        yield


def test_get_stats_overview():
    """Test global statistics calculation."""
    stats = stats_service.get_stats_overview()
    
    assert stats.total_transactions == 3
    assert stats.fraud_rate == pytest.approx(0.33333, rel=1e-2)
    assert stats.avg_amount == pytest.approx(1716.67, rel=1e-2)
    assert stats.most_common_type == "PAYMENT"


def test_get_amount_distribution():
    """Test amount distribution histogram."""
    distribution = stats_service.get_amount_distribution()
    
    assert len(distribution.bins) > 0
    assert len(distribution.counts) > 0
    assert len(distribution.bins) == len(distribution.counts)
    assert sum(distribution.counts) == 3


def test_get_stats_by_type():
    """Test statistics aggregation by type."""
    stats = stats_service.get_stats_by_type()
    
    assert len(stats) == 2
    payment_stat = next((s for s in stats if s.type == "PAYMENT"), None)
    assert payment_stat is not None
    assert payment_stat.count == 2
    assert payment_stat.avg_amount == 75.0


def test_get_daily_stats():
    """Test daily statistics aggregation."""
    daily = stats_service.get_daily_stats()
    
    assert len(daily) == 2
    step1 = next((s for s in daily if s.step == 1), None)
    assert step1 is not None
    assert step1.count == 2
    