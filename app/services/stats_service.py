"""
Statistics service for Banking Transactions API.

This module provides statistical analysis and aggregations on transaction data.
"""

from typing import List, Dict, Any
from collections import Counter, defaultdict
from statistics import mean
from app.utils.loader import load_transactions
from app.models.schemas import (
    StatsOverview,
    AmountDistribution,
    StatsByType,
    DailyStats,
)

_TRANSACTIONS: List[Dict[str, Any]] | None = None


def _get_data() -> List[Dict[str, Any]]:
    """
    Get cached transaction data.

    Returns
    -------
    List[Dict[str, Any]]
        List of transaction dictionaries
    """
    global _TRANSACTIONS
    if _TRANSACTIONS is None:
        _TRANSACTIONS = load_transactions()
    return _TRANSACTIONS


def get_stats_overview() -> StatsOverview:
    """
    Calculate global statistics overview.

    Returns
    -------
    StatsOverview
        Global statistics including total transactions, fraud rate, average amount
    """
    data = _get_data()
    total = len(data)

    if total == 0:
        return StatsOverview(
            total_transactions=0,
            fraud_rate=0.0,
            avg_amount=0.0,
            most_common_type="N/A"
        )

    frauds = [t for t in data if int(t.get("isFraud", 0)) == 1]
    avg_amount = mean(float(t.get("amount", 0)) for t in data)
    most_common_type = Counter(t.get("type") for t in data if t.get("type")).most_common(1)[0][0]

    return StatsOverview(
        total_transactions=total,
        fraud_rate=round(len(frauds) / total, 5),
        avg_amount=round(avg_amount, 2),
        most_common_type=most_common_type,
    )


def get_amount_distribution() -> AmountDistribution:
    """
    Calculate distribution of transaction amounts.

    Returns
    -------
    AmountDistribution
        Amount distribution with bins and counts
    """
    data = _get_data()

    if len(data) == 0:
        return AmountDistribution(bins=[], counts=[])

    bins = [
        (0, 100),
        (100, 500),
        (500, 1000),
        (1000, 5000),
        (5000, 10000),
        (10000, 50000),
        (50000, 100000),
        (100000, 500000),
        (500000, float('inf'))
    ]
    counts = []

    for low, high in bins:
        if high == float('inf'):
            count = sum(1 for t in data if float(t.get("amount", 0)) >= low)
        else:
            count = sum(1 for t in data if low <= float(t.get("amount", 0)) < high)
        counts.append(count)

    labels = []
    for low, high in bins:
        if high == float('inf'):
            labels.append(f"{low}+")
        else:
            labels.append(f"{low}-{high}")

    return AmountDistribution(
        bins=labels,
        counts=counts,
    )


def get_stats_by_type() -> List[StatsByType]:
    """
    Calculate statistics aggregated by transaction type.

    Returns
    -------
    List[StatsByType]
        Statistics for each transaction type
    """
    data = _get_data()

    if len(data) == 0:
        return []

    grouped: Dict[str, List[float]] = defaultdict(list)

    for t in data:
        tx_type = t.get("type")
        if tx_type:
            grouped[tx_type].append(float(t.get("amount", 0)))

    stats = []
    for tx_type, amounts in grouped.items():
        stats.append(
            StatsByType(
                type=tx_type,
                count=len(amounts),
                avg_amount=round(mean(amounts), 2),
                total_amount=round(sum(amounts), 2),
            )
        )

    # Sort by count descending
    stats.sort(key=lambda x: x.count, reverse=True)
    return stats


def get_daily_stats() -> List[DailyStats]:
    """
    Calculate daily aggregated statistics.

    Returns
    -------
    List[DailyStats]
        Statistics for each time step (day)
    """
    data = _get_data()

    if len(data) == 0:
        return []

    # Group by step (time step in the dataset)
    daily: Dict[int, List[float]] = defaultdict(list)

    for t in data:
        step = int(t.get("step", 0))
        daily[step].append(float(t.get("amount", 0)))

    stats = []
    for step, amounts in sorted(daily.items()):
        stats.append(
            DailyStats(
                step=step,
                count=len(amounts),
                avg_amount=round(mean(amounts), 2),
                total_amount=round(sum(amounts), 2),
            )
        )

    return stats