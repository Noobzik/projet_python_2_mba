"""Unit tests for stats_service."""

import pandas as pd

from banking_api.services import stats_service as svc


def test_get_overview(sample_df: pd.DataFrame) -> None:
    result = svc.get_overview(df=sample_df)
    assert result.total_transactions == 5
    assert 0.0 <= result.fraud_rate <= 1.0
    assert result.avg_amount > 0
    assert result.most_common_type in {"TRANSFER", "CASH_OUT", "PAYMENT"}


def test_get_overview_fraud_rate(sample_df: pd.DataFrame) -> None:
    result = svc.get_overview(df=sample_df)
    # 1 fraud out of 5 = 0.2
    assert abs(result.fraud_rate - 0.2) < 0.001


def test_get_amount_distribution(sample_df: pd.DataFrame) -> None:
    result = svc.get_amount_distribution(bins=5, df=sample_df)
    assert len(result.bins) == 5
    assert len(result.counts) == 5
    assert sum(result.counts) == 5


def test_get_stats_by_type(sample_df: pd.DataFrame) -> None:
    results = svc.get_stats_by_type(df=sample_df)
    types = [r.type for r in results]
    assert "TRANSFER" in types
    assert "CASH_OUT" in types
    for r in results:
        assert r.count > 0
        assert r.avg_amount > 0


def test_get_daily_stats(sample_df: pd.DataFrame) -> None:
    results = svc.get_daily_stats(df=sample_df)
    steps = [r.step for r in results]
    assert 1 in steps
    assert 2 in steps
    assert 3 in steps


def test_get_overview_empty_df() -> None:
    import pandas as pd
    empty = pd.DataFrame(
        columns=["step", "type", "amount", "isFraud", "isFlaggedFraud"]
    )
    result = svc.get_overview(df=empty)
    assert result.total_transactions == 0
    assert result.fraud_rate == 0.0
