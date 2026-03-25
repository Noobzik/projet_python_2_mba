"""Unit tests for transactions_service."""

import pytest
import pandas as pd

from banking_api.models.schemas import SearchRequest
from banking_api.services import transactions_service as svc


def test_list_transactions_returns_all(sample_df: pd.DataFrame) -> None:
    result = svc.list_transactions(page=1, limit=10, df=sample_df)
    assert result.total == 5
    assert len(result.transactions) == 5


def test_list_transactions_pagination(sample_df: pd.DataFrame) -> None:
    result = svc.list_transactions(page=1, limit=2, df=sample_df)
    assert len(result.transactions) == 2
    result2 = svc.list_transactions(page=2, limit=2, df=sample_df)
    assert len(result2.transactions) == 2


def test_list_transactions_filter_type(sample_df: pd.DataFrame) -> None:
    result = svc.list_transactions(type_filter="TRANSFER", df=sample_df)
    assert all(t.type == "TRANSFER" for t in result.transactions)


def test_list_transactions_filter_fraud(sample_df: pd.DataFrame) -> None:
    result = svc.list_transactions(is_fraud=1, df=sample_df)
    assert all(t.isFraud == 1 for t in result.transactions)
    assert result.total == 1


def test_list_transactions_filter_amount(sample_df: pd.DataFrame) -> None:
    result = svc.list_transactions(min_amount=500.0, max_amount=1000.0, df=sample_df)
    assert all(500.0 <= t.amount <= 1000.0 for t in result.transactions)


def test_get_transaction_by_id_found(sample_df: pd.DataFrame) -> None:
    result = svc.get_transaction_by_id("tx_0000001", df=sample_df)
    assert result is not None
    assert result.id == "tx_0000001"


def test_get_transaction_by_id_not_found(sample_df: pd.DataFrame) -> None:
    result = svc.get_transaction_by_id("tx_9999999", df=sample_df)
    assert result is None


def test_search_transactions_by_type(sample_df: pd.DataFrame) -> None:
    req = SearchRequest(type="CASH_OUT")
    results = svc.search_transactions(req, df=sample_df)
    assert all(r.type == "CASH_OUT" for r in results)


def test_search_transactions_amount_range(sample_df: pd.DataFrame) -> None:
    req = SearchRequest(amount_range=[100.0, 600.0])
    results = svc.search_transactions(req, df=sample_df)
    assert all(100.0 <= r.amount <= 600.0 for r in results)


def test_search_transactions_fraud(sample_df: pd.DataFrame) -> None:
    req = SearchRequest(isFraud=1)
    results = svc.search_transactions(req, df=sample_df)
    assert len(results) == 1
    assert results[0].isFraud == 1


def test_get_transaction_types(sample_df: pd.DataFrame) -> None:
    types = svc.get_transaction_types(df=sample_df)
    assert "TRANSFER" in types
    assert "CASH_OUT" in types
    assert "PAYMENT" in types


def test_get_recent_transactions(sample_df: pd.DataFrame) -> None:
    results = svc.get_recent_transactions(n=3, df=sample_df)
    assert len(results) == 3


def test_get_transactions_by_customer(sample_df: pd.DataFrame) -> None:
    results = svc.get_transactions_by_customer("C001", df=sample_df)
    assert len(results) == 2
    assert all(r.nameOrig == "C001" for r in results)


def test_get_transactions_to_customer(sample_df: pd.DataFrame) -> None:
    results = svc.get_transactions_to_customer("C010", df=sample_df)
    assert len(results) == 1
    assert results[0].nameDest == "C010"
