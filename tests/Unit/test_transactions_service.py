"""
Unit tests for transactions service.

This module tests the business logic for transaction operations.
"""

import pytest
from unittest.mock import patch
from app.services import transactions_service
from app.models.schemas import TransactionSearchRequest


@pytest.fixture
def mock_transactions():
    """Mock transaction data for testing."""
    return [
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
        {
            "id": "tx_0000002",
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
            "id": "tx_0000003",
            "step": 2,
            "type": "CASH_OUT",
            "amount": 200.0,
            "nameOrig": "C001",
            "oldbalanceOrg": 900.0,
            "newbalanceOrig": 700.0,
            "nameDest": "M002",
            "oldbalanceDest": 0.0,
            "newbalanceDest": 0.0,
            "isFraud": 0,
            "isFlaggedFraud": 0,
        },
    ]


@pytest.fixture(autouse=True)
def setup_mock_data(mock_transactions):
    """Setup mock data before each test."""
    with patch.object(transactions_service, '_get_data', return_value=mock_transactions):
        transactions_service._TRANSACTIONS = mock_transactions
        yield


def test_get_transactions_pagination():
    """Test pagination functionality."""
    result = transactions_service.get_transactions(page=1, limit=2, tx_type=None, is_fraud=None, min_amount=None, max_amount=None)
    
    assert result.page == 1
    assert result.limit == 2
    assert result.total == 3
    assert len(result.transactions) == 2


def test_get_transactions_with_type_filter():
    """Test filtering by transaction type."""
    result = transactions_service.get_transactions(page=1, limit=10, tx_type="PAYMENT", is_fraud=None, min_amount=None, max_amount=None)
    
    assert result.total == 1
    assert all(t.type == "PAYMENT" for t in result.transactions)


def test_get_transactions_with_fraud_filter():
    """Test filtering by fraud status."""
    result = transactions_service.get_transactions(page=1, limit=10, tx_type=None, is_fraud=1, min_amount=None, max_amount=None)
    
    assert result.total == 1
    assert all(t.isFraud == 1 for t in result.transactions)


def test_get_transactions_with_amount_filter():
    """Test filtering by amount range."""
    result = transactions_service.get_transactions(page=1, limit=10, tx_type=None, is_fraud=None, min_amount=100, max_amount=5000)
    
    assert result.total == 3
    assert all(100 <= t.amount <= 5000 for t in result.transactions)


def test_get_transaction_by_id():
    """Test retrieving transaction by ID."""
    transaction = transactions_service.get_transaction_by_id("tx_0000001")
    
    assert transaction is not None
    assert transaction["id"] == "tx_0000001"
    assert transaction["amount"] == 100.0


def test_get_transaction_by_invalid_id():
    """Test retrieving with invalid ID."""
    transaction = transactions_service.get_transaction_by_id("tx_9999999")
    
    assert transaction is None


def test_search_transactions():
    """Test multi-criteria search."""
    request = TransactionSearchRequest(type="TRANSFER", isFraud=1)
    results = transactions_service.search_transactions(request.dict(exclude_none=True))
    
    assert len(results) == 1
    assert all(t.type == "TRANSFER" for t in results)
    assert all(t.isFraud == 1 for t in results)


def test_get_transaction_types():
    """Test getting unique transaction types."""
    types = transactions_service.get_transaction_types()
    
    assert len(types) == 3
    assert "PAYMENT" in types
    assert "TRANSFER" in types
    assert "CASH_OUT" in types


def test_get_recent_transactions():
    """Test getting recent transactions."""
    recent = transactions_service.get_recent_transactions(n=2)
    
    assert len(recent) == 2


def test_delete_transaction():
    """Test transaction deletion."""
    result = transactions_service.delete_transaction("tx_0000001")
    
    assert result is True


def test_delete_nonexistent_transaction():
    """Test deleting nonexistent transaction."""
    result = transactions_service.delete_transaction("tx_9999999")
    
    assert result is False


def test_get_transactions_by_customer():
    """Test getting transactions by customer origin."""
    transactions = transactions_service.get_transactions_by_customer("C001")
    
    assert len(transactions) == 2
    assert all(t.nameOrig == "C001" for t in transactions)


def test_get_transactions_to_customer():
    """Test getting transactions by customer destination."""
    transactions = transactions_service.get_transactions_to_customer("M001")
    
    assert len(transactions) == 1
    assert all(t.nameDest == "M001" for t in transactions)