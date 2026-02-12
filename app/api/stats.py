"""
Statistics router for Banking Transactions API.

This module defines the API endpoints for statistical analysis.
"""

from fastapi import APIRouter
from typing import List
from app.models.schemas import (
    StatsOverview,
    AmountDistribution,
    StatsByType,
    DailyStats,
)
from app.services.stats_service import (
    get_stats_overview,
    get_amount_distribution,
    get_stats_by_type,
    get_daily_stats,
)

router = APIRouter(tags=["Statistics"])


# 9️⃣ GET /api/stats/overview
@router.get("/stats/overview", response_model=StatsOverview)
def overview() -> StatsOverview:
    """
    Get global statistics overview.

    Returns
    -------
    StatsOverview
        Global statistics including:
        - Total number of transactions
        - Fraud rate (percentage)
        - Average transaction amount
        - Most common transaction type
    """
    return get_stats_overview()


# 🔟 GET /api/stats/amount-distribution
@router.get("/stats/amount-distribution", response_model=AmountDistribution)
def distribution() -> AmountDistribution:
    """
    Get histogram of transaction amounts.

    Returns
    -------
    AmountDistribution
        Distribution of amounts in predefined bins with counts
    """
    return get_amount_distribution()


# 1️⃣1️⃣ GET /api/stats/by-type
@router.get("/stats/by-type", response_model=List[StatsByType])
def by_type() -> List[StatsByType]:
    """
    Get statistics aggregated by transaction type.

    Returns
    -------
    List[StatsByType]
        Statistics for each transaction type including:
        - Transaction count
        - Average amount
        - Total amount
    """
    return get_stats_by_type()


# 1️⃣2️⃣ GET /api/stats/daily
@router.get("/stats/daily", response_model=List[DailyStats])
def daily() -> List[DailyStats]:
    """
    Get average and volume of transactions by day (step).

    Returns
    -------
    List[DailyStats]
        Daily statistics including:
        - Time step (day)
        - Transaction count
        - Average amount
        - Total amount
    """
    return get_daily_stats()