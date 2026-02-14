from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TransactionSearchIn(BaseModel):
    """
    Search criteria for transactions.

    All fields are optional. When multiple criteria are provided,
    they are combined with AND logic.
    """

    type: Optional[str] = Field(default=None, examples=["TRANSFER"])
    isFraud: Optional[bool] = Field(default=None, examples=[True])
    min_amount: Optional[float] = Field(default=None, ge=0, examples=[10.0])
    max_amount: Optional[float] = Field(default=None, ge=0, examples=[1000.0])
    nameOrig: Optional[str] = Field(default=None, examples=["C1"])
    nameDest: Optional[str] = Field(default=None, examples=["C2"])
