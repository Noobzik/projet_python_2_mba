from __future__ import annotations

from pydantic import BaseModel, Field


class StatsOverviewOut(BaseModel):
    total_transactions: int = Field(..., ge=0)
    fraud_rate: float = Field(..., ge=0, le=1)
    avg_amount: float = Field(..., ge=0)
    most_common_type: str | None


class AmountDistributionBucket(BaseModel):
    range: str
    count: int = Field(..., ge=0)


class AmountDistributionOut(BaseModel):
    buckets: list[AmountDistributionBucket]


class ByTypeItem(BaseModel):
    type: str
    count: int = Field(..., ge=0)
    avg_amount: float = Field(..., ge=0)


class ByTypeOut(BaseModel):
    items: list[ByTypeItem]


class DailyItem(BaseModel):
    step: int = Field(..., ge=0)
    count: int = Field(..., ge=0)
    avg_amount: float = Field(..., ge=0)


class DailyOut(BaseModel):
    items: list[DailyItem]
