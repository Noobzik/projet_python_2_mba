"""
Statistics Router.

Exposes endpoints 9–12 for global and per-type analytics.
"""

from fastapi import APIRouter, Query

from banking_api.models.schemas import (
    AmountDistribution,
    DailyStat,
    OverviewStats,
    TypeStat,
)
from banking_api.services import stats_service as svc

router: APIRouter = APIRouter()


@router.get("/overview", response_model=OverviewStats, summary="Global statistics")
def get_overview() -> OverviewStats:
    """Return global dataset statistics.

    Returns
    -------
    OverviewStats
        Total transactions, fraud rate, average amount and most common type.
    """
    return svc.get_overview()


@router.get(
    "/amount-distribution",
    response_model=AmountDistribution,
    summary="Amount histogram",
)
def get_amount_distribution(
    bins: int = Query(default=10, ge=2, le=100, description="Number of histogram bins"),
) -> AmountDistribution:
    """Return a histogram of transaction amounts split into *bins* classes.

    Parameters
    ----------
    bins : int
        Number of histogram bins (default 10).

    Returns
    -------
    AmountDistribution
        Bin labels and their respective transaction counts.
    """
    return svc.get_amount_distribution(bins=bins)


@router.get(
    "/by-type",
    response_model=list[TypeStat],
    summary="Statistics by transaction type",
)
def get_stats_by_type() -> list[TypeStat]:
    """Return transaction count and average amount grouped by type.

    Returns
    -------
    list[TypeStat]
        One entry per unique transaction type.
    """
    return svc.get_stats_by_type()


@router.get(
    "/daily",
    response_model=list[DailyStat],
    summary="Daily statistics",
)
def get_daily_stats() -> list[DailyStat]:
    """Return average amount and volume grouped by step (day proxy).

    Returns
    -------
    list[DailyStat]
        One entry per unique step value.
    """
    return svc.get_daily_stats()
