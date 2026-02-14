from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CustomerOut(BaseModel):
    id: str = Field(..., examples=["C123456"])
    transaction_count: Optional[int] = Field(default=None, examples=[42])


class CustomerProfileOut(BaseModel):
    id: str = Field(..., examples=["C123456"])
    total_sent: float = Field(..., ge=0, examples=[1200.0])
    total_received: float = Field(..., ge=0, examples=[800.0])
    transaction_count_as_origin: int = Field(..., ge=0, examples=[10])
    transaction_count_as_destination: int = Field(..., ge=0, examples=[5])


class TopCustomersOut(BaseModel):
    n: int = Field(..., ge=1, examples=[10])
    customers: list[CustomerOut]
