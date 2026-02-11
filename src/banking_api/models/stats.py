"""Statistical data models.

This module defines Pydantic models for statistical responses.
"""

from typing import List
from pydantic import BaseModel, Field


class StatsOverview(BaseModel):
    """Overall statistics of the dataset.

    Parameters
    ----------
    total_transactions : int
        Total number of transactions.
    fraud_rate : float
        Rate of fraudulent transactions.
    avg_amount : float
        Average transaction amount.
    most_common_type : str
        Most common transaction type.
    total_amount : float
        Total amount of all transactions.
    """

    total_transactions: int = Field(..., ge=0)
    fraud_rate: float = Field(..., ge=0.0, le=1.0)
    avg_amount: float = Field(..., ge=0.0)
    most_common_type: str
    total_amount: float = Field(..., ge=0.0)


class AmountDistribution(BaseModel):
    """Distribution of transaction amounts.

    Parameters
    ----------
    bins : List[str]
        Bin labels (e.g., "0-100", "100-500").
    counts : List[int]
        Count of transactions in each bin.
    """

    bins: List[str]
    counts: List[int]


class TypeStats(BaseModel):
    """Statistics for a transaction type.

    Parameters
    ----------
    type : str
        Transaction type.
    count : int
        Number of transactions.
    avg_amount : float
        Average amount for this type.
    total_amount : float
        Total amount for this type.
    fraud_rate : float
        Fraud rate for this type.
    """

    type: str
    count: int = Field(..., ge=0)
    avg_amount: float = Field(..., ge=0.0)
    total_amount: float = Field(..., ge=0.0)
    fraud_rate: float = Field(..., ge=0.0, le=1.0)


class DailyStats(BaseModel):
    """Daily statistics.

    Parameters
    ----------
    step : str
        Date (day).
    count : int
        Number of transactions.
    avg_amount : float
        Average transaction amount.
    total_amount : float
        Total transaction amount.
    fraud_count : int
        Number of fraudulent transactions.
    """

    step: str
    count: int = Field(..., ge=0)
    avg_amount: float = Field(..., ge=0.0)
    total_amount: float = Field(..., ge=0.0)
    fraud_count: int = Field(..., ge=0)


class FraudSummary(BaseModel):
    """Summary of fraud statistics.

    Parameters
    ----------
    total_frauds : int
        Total number of fraudulent transactions.
    flagged : int
        Number of flagged frauds.
    fraud_rate : float
        Overall fraud rate.
    total_fraud_amount : float
        Total amount of fraudulent transactions.
    """

    total_frauds: int = Field(..., ge=0)
    flagged: int = Field(..., ge=0)
    fraud_rate: float = Field(..., ge=0.0, le=1.0)
    total_fraud_amount: float = Field(..., ge=0.0)


class FraudByType(BaseModel):
    """Fraud statistics by transaction type.

    Parameters
    ----------
    type : str
        Transaction type.
    fraud_rate : float
        Fraud rate for this type.
    fraud_count : int
        Number of frauds for this type.
    total_count : int
        Total transactions for this type.
    """

    type: str
    fraud_rate: float = Field(..., ge=0.0, le=1.0)
    fraud_count: int = Field(..., ge=0)
    total_count: int = Field(..., ge=0)
