"""Unit tests for service layer.

This module tests business logic in service classes.
"""

import pytest
import pandas as pd
from src.banking_api.services.transactions_service import TransactionsService
from src.banking_api.services.stats_service import StatsService
from src.banking_api.services.fraud_detection_service import FraudDetectionService
from src.banking_api.services.customer_service import CustomerService
from src.banking_api.services.system_service import SystemService
from src.banking_api.models.transaction import (
    TransactionSearch,
    FraudPredictionRequest
)


def test_transactions_service_get_transactions(load_sample_data: None) -> None:
    """Test TransactionsService.get_transactions method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = TransactionsService()
    result = service.get_transactions(page=1, limit=10)
    assert result.page == 1
    assert result.limit == 10
    assert len(result.transactions) > 0


def test_transactions_service_get_by_id(load_sample_data: None) -> None:
    """Test TransactionsService.get_transaction_by_id method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = TransactionsService()
    transaction = service.get_transaction_by_id("tx_0000000")
    assert transaction is not None
    assert transaction.id == "tx_0000000"


def test_transactions_service_search(load_sample_data: None) -> None:
    """Test TransactionsService.search_transactions method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = TransactionsService()
    criteria = TransactionSearch(use_chip="Swipe")
    result = service.search_transactions(criteria, page=1, limit=10)
    assert result.total >= 0
    for tx in result.transactions:
        assert "Swipe" in tx.use_chip


def test_stats_service_overview(load_sample_data: None) -> None:
    """Test StatsService.get_overview method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = StatsService()
    overview = service.get_overview()
    assert overview.total_transactions > 0
    assert 0.0 <= overview.fraud_rate <= 1.0
    assert overview.avg_amount >= 0.0


def test_stats_service_by_type(load_sample_data: None) -> None:
    """Test StatsService.get_stats_by_type method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = StatsService()
    stats = service.get_stats_by_type()
    assert len(stats) > 0
    for stat in stats:
        assert stat.count > 0
        assert stat.avg_amount >= 0.0


def test_fraud_service_summary(load_sample_data: None) -> None:
    """Test FraudDetectionService.get_fraud_summary method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = FraudDetectionService()
    summary = service.get_fraud_summary()
    assert summary.total_frauds >= 0
    assert 0.0 <= summary.fraud_rate <= 1.0


def test_fraud_service_predict(load_sample_data: None) -> None:
    """Test FraudDetectionService.predict_fraud method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = FraudDetectionService()
    request = FraudPredictionRequest(
        amount=100.0,
        use_chip="Chip Transaction",
        merchant_state="ND",
        mcc=5411
    )
    result = service.predict_fraud(request)
    assert isinstance(result.isFraud, bool)
    assert 0.0 <= result.probability <= 1.0


def test_customer_service_get_customers(load_sample_data: None) -> None:
    """Test CustomerService.get_customers method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = CustomerService()
    result = service.get_customers(page=1, limit=10)
    assert result.page == 1
    assert len(result.customers) > 0


def test_customer_service_get_profile(load_sample_data: None) -> None:
    """Test CustomerService.get_customer_profile method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = CustomerService()
    profile = service.get_customer_profile(1556)
    assert profile.id == 1556
    assert profile.transactions_count > 0


def test_customer_service_top_customers(load_sample_data: None) -> None:
    """Test CustomerService.get_top_customers method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = CustomerService()
    top_customers = service.get_top_customers(n=3)
    assert len(top_customers) <= 3
    if len(top_customers) > 1:
        assert top_customers[0].total_amount >= top_customers[1].total_amount


def test_system_service_health(load_sample_data: None) -> None:
    """Test SystemService.get_health method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = SystemService()
    health = service.get_health()
    assert health.status in ["ok", "degraded", "error"]
    assert health.dataset_loaded is True


def test_system_service_metadata(load_sample_data: None) -> None:
    """Test SystemService.get_metadata method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = SystemService()
    metadata = service.get_metadata()
    assert metadata.version == "1.0.0"
    assert metadata.endpoints_count == 20
