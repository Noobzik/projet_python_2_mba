"""Unit tests for customer_service."""

import pandas as pd

from banking_api.services import customer_service as svc


def test_list_customers(sample_df: pd.DataFrame) -> None:
    results = svc.list_customers(page=1, limit=10, df=sample_df)
    ids = [r.id for r in results]
    assert "C001" in ids
    assert "C002" in ids


def test_list_customers_pagination(sample_df: pd.DataFrame) -> None:
    page1 = svc.list_customers(page=1, limit=2, df=sample_df)
    page2 = svc.list_customers(page=2, limit=2, df=sample_df)
    assert len(page1) == 2
    assert len(page2) >= 1


def test_get_customer_profile_found(sample_df: pd.DataFrame) -> None:
    profile = svc.get_customer_profile("C001", df=sample_df)
    assert profile is not None
    assert profile.id == "C001"
    assert profile.transactions_count == 2
    assert profile.avg_amount > 0


def test_get_customer_profile_not_found(sample_df: pd.DataFrame) -> None:
    profile = svc.get_customer_profile("UNKNOWN", df=sample_df)
    assert profile is None


def test_get_customer_profile_fraud_flag(sample_df: pd.DataFrame) -> None:
    profile = svc.get_customer_profile("C003", df=sample_df)
    assert profile is not None
    assert profile.fraudulent is True


def test_get_top_customers(sample_df: pd.DataFrame) -> None:
    results = svc.get_top_customers(n=3, df=sample_df)
    assert len(results) <= 3
    volumes = [r.total_volume for r in results]
    assert volumes == sorted(volumes, reverse=True)
