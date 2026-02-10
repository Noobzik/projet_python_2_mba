"""Statistics routes.

This module defines API endpoints for statistical operations.
"""

from typing import List
from fastapi import APIRouter, Query
from ..models.stats import (
    StatsOverview,
    AmountDistribution,
    TypeStats,
    DailyStats
)
from ..services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["statistics"])
service = StatsService()


@router.get("/overview", response_model=StatsOverview)
def get_stats_overview() -> StatsOverview:
    """Get overall statistics of the dataset.

    Returns
    -------
    StatsOverview
        Overall statistics including total transactions,
        fraud rate, and average amount.
    """
    return service.get_overview()


@router.get("/amount-distribution", response_model=AmountDistribution)
def get_amount_distribution(
    bins: int = Query(10, ge=5, le=50, description="Number of bins")
) -> AmountDistribution:
    """Get distribution of transaction amounts.

    Parameters
    ----------
    bins : int
        Number of histogram bins (default: 10, range: 5-50).

    Returns
    -------
    AmountDistribution
        Distribution with bin labels and counts.
    """
    return service.get_amount_distribution(num_bins=bins)


@router.get("/by-type", response_model=List[TypeStats])
def get_stats_by_type() -> List[TypeStats]:
    """Get statistics grouped by transaction type.

    Returns
    -------
    List[TypeStats]
        List of statistics for each transaction type.
    """
    return service.get_stats_by_type()


@router.get("/daily", response_model=List[DailyStats])
def get_daily_stats(
    limit: int = Query(30, ge=0, le=365, description="Number of days (0 for all)")
) -> List[DailyStats]:
    """Get statistics grouped by day (step).

    Parameters
    ----------
    limit : int
        Maximum number of days to return (default: 30, 0 for all).

    Returns
    -------
    List[DailyStats]
        List of daily statistics including counts and averages.
    """
    return service.get_daily_stats(limit=limit)
