from __future__ import annotations

from fastapi import APIRouter, HTTPException

from banking_api.models.stats import AmountDistributionOut, ByTypeOut, DailyOut, StatsOverviewOut
from banking_api.services.stats_service import (
    amount_distribution,
    stats_by_type,
    stats_daily,
    stats_overview,
)

router = APIRouter()


@router.get("/stats/overview", response_model=StatsOverviewOut)
def overview() -> StatsOverviewOut:
    try:
        return stats_overview()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/stats/amount-distribution", response_model=AmountDistributionOut)
def distribution() -> AmountDistributionOut:
    try:
        return amount_distribution()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/stats/by-type", response_model=ByTypeOut)
def by_type() -> ByTypeOut:
    try:
        return stats_by_type()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/stats/daily", response_model=DailyOut)
def daily() -> DailyOut:
    try:
        return stats_daily()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
