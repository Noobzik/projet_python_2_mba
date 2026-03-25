"""
Statistics Service.

Computes aggregated and analytical metrics on the transactions dataset.
"""

from typing import Optional
import numpy as np
import pandas as pd

from banking_api.models.schemas import (
    AmountDistribution,
    DailyStat,
    OverviewStats,
    TypeStat,
)
from banking_api.services.data_loader import DataLoader


def _get_df(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Return provided DataFrame or singleton dataset.

    Parameters
    ----------
    df : pd.DataFrame or None
        Caller-supplied DataFrame (tests) or ``None``.

    Returns
    -------
    pd.DataFrame
        Active dataset.
    """
    return df if df is not None else DataLoader.get_instance().df


def get_overview(df: Optional[pd.DataFrame] = None) -> OverviewStats:
    """Compute global dataset statistics.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    OverviewStats
        Total count, fraud rate, average amount and most common type.
    """
    data: pd.DataFrame = _get_df(df)
    total: int = len(data)
    fraud_rate: float = float(data["isFraud"].mean()) if total else 0.0
    avg_amount: float = float(data["amount"].mean()) if total else 0.0
    most_common: str = (
        str(data["type"].mode().iloc[0]) if total else "N/A"
    )
    return OverviewStats(
        total_transactions=total,
        fraud_rate=round(fraud_rate, 5),
        avg_amount=round(avg_amount, 2),
        most_common_type=most_common,
    )


def get_amount_distribution(
    bins: int = 10,
    df: Optional[pd.DataFrame] = None,
) -> AmountDistribution:
    """Build a histogram of transaction amounts.

    Parameters
    ----------
    bins : int
        Number of histogram bins (default 10).
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    AmountDistribution
        Bin labels and corresponding counts.
    """
    data: pd.DataFrame = _get_df(df)
    amounts: pd.Series = data["amount"]  # type: ignore[type-arg]

    counts_arr: np.ndarray  # type: ignore[type-arg]
    edges: np.ndarray  # type: ignore[type-arg]
    counts_arr, edges = np.histogram(amounts, bins=bins)

    labels: list[str] = [
        f"{int(edges[i])}-{int(edges[i + 1])}" for i in range(len(edges) - 1)
    ]
    return AmountDistribution(bins=labels, counts=counts_arr.tolist())


def get_stats_by_type(df: Optional[pd.DataFrame] = None) -> list[TypeStat]:
    """Return count and average amount grouped by transaction type.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[TypeStat]
        One entry per unique transaction type.
    """
    data: pd.DataFrame = _get_df(df)
    grouped: pd.DataFrame = (
        data.groupby("type")["amount"]
        .agg(count="count", avg_amount="mean")
        .reset_index()
    )
    return [
        TypeStat(
            type=str(row["type"]),
            count=int(row["count"]),
            avg_amount=round(float(row["avg_amount"]), 2),
        )
        for _, row in grouped.iterrows()
    ]


def get_daily_stats(df: Optional[pd.DataFrame] = None) -> list[DailyStat]:
    """Return average amount and volume grouped by ``step``.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[DailyStat]
        One entry per unique step value.
    """
    data: pd.DataFrame = _get_df(df)
    grouped: pd.DataFrame = (
        data.groupby("step")["amount"]
        .agg(count="count", avg_amount="mean")
        .reset_index()
    )
    return [
        DailyStat(
            step=int(row["step"]),
            count=int(row["count"]),
            avg_amount=round(float(row["avg_amount"]), 2),
        )
        for _, row in grouped.iterrows()
    ]
