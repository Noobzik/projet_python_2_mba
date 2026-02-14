from __future__ import annotations

from pydantic import BaseModel, Field

from banking_api.models.transaction import TransactionOut


class FraudSummaryOut(BaseModel):
    total_transactions: int = Field(..., ge=0)
    total_frauds: int = Field(..., ge=0)
    flagged_frauds: int = Field(..., ge=0)
    fraud_rate: float = Field(..., ge=0, le=1)
    flagged_rate: float = Field(..., ge=0, le=1)


class FraudTransactionListOut(BaseModel):
    page: int = Field(..., ge=1)
    transactions: list[TransactionOut]


class FraudCustomerOut(BaseModel):
    id: str
    fraud_count: int = Field(..., ge=0)


class FraudTopCustomersOut(BaseModel):
    n: int = Field(..., ge=1)
    customers: list[FraudCustomerOut]
