"""
Pydantic models (schemas) used across the Banking Transactions API.

All request bodies and shared response shapes are defined here so that
routers and services can import them without circular dependencies.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Transaction schemas
# ---------------------------------------------------------------------------


class TransactionOut(BaseModel):
    """Single transaction response shape."""

    id: str
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    isFraud: int
    isFlaggedFraud: int


class PaginatedTransactions(BaseModel):
    """Paginated list of transactions."""

    page: int
    limit: int
    total: int
    transactions: list[TransactionOut]


class SearchRequest(BaseModel):
    """Body for POST /api/transactions/search."""

    type: Optional[str] = None
    isFraud: Optional[int] = None
    amount_range: Optional[list[float]] = Field(
        default=None, min_length=2, max_length=2
    )
    nameOrig: Optional[str] = None
    nameDest: Optional[str] = None


# ---------------------------------------------------------------------------
# Statistics schemas
# ---------------------------------------------------------------------------


class OverviewStats(BaseModel):
    """Global dataset statistics."""

    total_transactions: int
    fraud_rate: float
    avg_amount: float
    most_common_type: str


class AmountDistribution(BaseModel):
    """Histogram of transaction amounts."""

    bins: list[str]
    counts: list[int]


class TypeStat(BaseModel):
    """Statistics per transaction type."""

    type: str
    count: int
    avg_amount: float


class DailyStat(BaseModel):
    """Statistics per step (day proxy)."""

    step: int
    count: int
    avg_amount: float


# ---------------------------------------------------------------------------
# Fraud schemas
# ---------------------------------------------------------------------------


class FraudSummary(BaseModel):
    """Fraud overview."""

    total_frauds: int
    flagged: int
    precision: float
    recall: float


class FraudByType(BaseModel):
    """Fraud rate per transaction type."""

    type: str
    total: int
    fraud_count: int
    fraud_rate: float


class FraudPredictRequest(BaseModel):
    """Body for POST /api/fraud/predict."""

    type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float


class FraudPredictResponse(BaseModel):
    """Fraud prediction result."""

    isFraud: bool
    probability: float


# ---------------------------------------------------------------------------
# Customer schemas
# ---------------------------------------------------------------------------


class CustomerSummary(BaseModel):
    """Lightweight customer record for paginated list."""

    id: str
    transactions_count: int


class CustomerProfile(BaseModel):
    """Detailed customer profile."""

    id: str
    transactions_count: int
    avg_amount: float
    fraudulent: bool


class TopCustomer(BaseModel):
    """Customer ranked by transaction volume."""

    id: str
    total_volume: float
    transactions_count: int


# ---------------------------------------------------------------------------
# System schemas
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    """Health-check response."""

    status: str
    uptime: str
    dataset_loaded: bool


class MetadataResponse(BaseModel):
    """Service metadata."""

    version: str
    last_update: str


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------


class MessageResponse(BaseModel):
    """Generic acknowledgement message."""

    message: str
    detail: Optional[Any] = None
