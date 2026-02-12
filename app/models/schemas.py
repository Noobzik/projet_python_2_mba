"""
Pydantic models for the Banking Transactions API.

This module defines all the data models used throughout the API for request
validation, response serialization, and data transfer.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class TransactionType(str, Enum):
    """Enumeration of available transaction types."""

    PAYMENT = "PAYMENT"
    TRANSFER = "TRANSFER"
    CASH_OUT = "CASH_OUT"
    DEBIT = "DEBIT"
    CASH_IN = "CASH_IN"


class Transaction(BaseModel):
    """
    Model representing a bank transaction.

    Attributes
    ----------
    step : int
        Time step of the transaction
    type : str
        Type of transaction
    amount : float
        Transaction amount
    nameOrig : str
        Customer ID initiating the transaction
    oldbalanceOrg : float
        Initial balance before transaction
    newbalanceOrig : float
        New balance after transaction
    nameDest : str
        Recipient customer ID
    oldbalanceDest : float
        Initial recipient balance
    newbalanceDest : float
        New recipient balance
    isFraud : int
        Fraud flag (0 or 1)
    isFlaggedFraud : int
        Flagged fraud indicator (0 or 1)
    """

    model_config = ConfigDict(from_attributes=True)

    step: int = Field(..., description="Time step")
    type: str = Field(..., description="Transaction type")
    amount: float = Field(..., ge=0, description="Transaction amount")
    nameOrig: str = Field(..., description="Origin customer ID")
    oldbalanceOrg: float = Field(..., ge=0, description="Origin old balance")
    newbalanceOrig: float = Field(..., ge=0, description="Origin new balance")
    nameDest: str = Field(..., description="Destination customer ID")
    oldbalanceDest: float = Field(..., ge=0, description="Destination old balance")
    newbalanceDest: float = Field(..., ge=0, description="Destination new balance")
    isFraud: int = Field(..., ge=0, le=1, description="Fraud indicator")
    isFlaggedFraud: int = Field(..., ge=0, le=1, description="Flagged fraud indicator")


class TransactionResponse(BaseModel):
    """
    Response model for a single transaction with ID.

    Attributes
    ----------
    id : str
        Unique transaction identifier
    """

    model_config = ConfigDict(from_attributes=True)

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


class PaginatedTransactionsResponse(BaseModel):
    """
    Paginated response for transaction lists.

    Attributes
    ----------
    page : int
        Current page number
    limit : int
        Number of items per page
    total : int
        Total number of transactions
    transactions : List[TransactionResponse]
        List of transactions for current page
    """

    page: int = Field(..., ge=1, description="Current page")
    limit: int = Field(..., ge=1, le=1000, description="Items per page")
    total: int = Field(..., ge=0, description="Total items")
    transactions: List[TransactionResponse] = Field(..., description="Transaction list")


class TransactionSearchRequest(BaseModel):
    """
    Request model for multi-criteria transaction search.

    Attributes
    ----------
    type : Optional[str]
        Filter by transaction type
    isFraud : Optional[int]
        Filter by fraud status
    amount_range : Optional[List[float]]
        Filter by amount range [min, max]
    customer_id : Optional[str]
        Filter by customer ID
    """

    type: Optional[str] = Field(None, description="Transaction type filter")
    isFraud: Optional[int] = Field(None, ge=0, le=1, description="Fraud filter")
    amount_range: Optional[List[float]] = Field(None, description="Amount range [min, max]")
    customer_id: Optional[str] = Field(None, description="Customer ID filter")


class StatsOverview(BaseModel):
    """
    Global statistics overview.

    Attributes
    ----------
    total_transactions : int
        Total number of transactions
    fraud_rate : float
        Percentage of fraudulent transactions
    avg_amount : float
        Average transaction amount
    most_common_type : str
        Most frequent transaction type
    """

    total_transactions: int
    fraud_rate: float
    avg_amount: float
    most_common_type: str


class AmountDistribution(BaseModel):
    """
    Distribution of transaction amounts by bins.

    Attributes
    ----------
    bins : List[str]
        Amount range labels
    counts : List[int]
        Number of transactions in each bin
    """

    bins: List[str]
    counts: List[int]


class StatsByType(BaseModel):
    """
    Statistics aggregated by transaction type.

    Attributes
    ----------
    type : str
        Transaction type
    count : int
        Number of transactions
    avg_amount : float
        Average amount for this type
    total_amount : float
        Total amount for this type
    """

    type: str
    count: int
    avg_amount: float
    total_amount: float


class DailyStats(BaseModel):
    """
    Daily aggregated statistics.

    Attributes
    ----------
    step : int
        Time step (day)
    count : int
        Number of transactions
    avg_amount : float
        Average amount
    total_amount : float
        Total amount
    """

    step: int
    count: int
    avg_amount: float
    total_amount: float


class FraudSummary(BaseModel):
    """
    Fraud detection summary.

    Attributes
    ----------
    total_frauds : int
        Total fraudulent transactions
    flagged : int
        Number of flagged transactions
    precision : float
        Detection precision
    recall : float
        Detection recall
    """

    total_frauds: int
    flagged: int
    precision: float
    recall: float


class FraudByType(BaseModel):
    """
    Fraud rate by transaction type.

    Attributes
    ----------
    type : str
        Transaction type
    total_count : int
        Total transactions of this type
    fraud_count : int
        Fraudulent transactions
    fraud_rate : float
        Fraud percentage
    """

    type: str
    total_count: int
    fraud_count: int
    fraud_rate: float


class FraudPredictionRequest(BaseModel):
    """
    Request for fraud prediction.

    Attributes
    ----------
    type : str
        Transaction type
    amount : float
        Transaction amount
    oldbalanceOrg : float
        Origin balance before
    newbalanceOrig : float
        Origin balance after
    """

    type: str
    amount: float = Field(..., ge=0)
    oldbalanceOrg: float = Field(..., ge=0)
    newbalanceOrig: float = Field(..., ge=0)


class FraudPredictionResponse(BaseModel):
    """
    Response for fraud prediction.

    Attributes
    ----------
    isFraud : bool
        Predicted fraud status
    probability : float
        Fraud probability score
    """

    isFraud: bool
    probability: float = Field(..., ge=0, le=1)


class Customer(BaseModel):
    """
    Customer profile information.

    Attributes
    ----------
    id : str
        Customer unique identifier
    transactions_count : int
        Number of transactions
    avg_amount : float
        Average transaction amount
    total_amount : float
        Total transaction amount
    fraudulent : bool
        Whether involved in fraud
    """

    id: str
    transactions_count: int
    avg_amount: float
    total_amount: float
    fraudulent: bool


class PaginatedCustomersResponse(BaseModel):
    """
    Paginated response for customer lists.

    Attributes
    ----------
    page : int
        Current page number
    limit : int
        Items per page
    total : int
        Total customers
    customers : List[str]
        Customer ID list
    """

    page: int
    limit: int
    total: int
    customers: List[str]


class TopCustomer(BaseModel):
    """
    Top customer by transaction volume.

    Attributes
    ----------
    customer_id : str
        Customer identifier
    total_amount : float
        Total transaction volume
    transaction_count : int
        Number of transactions
    """

    customer_id: str
    total_amount: float
    transaction_count: int


class HealthResponse(BaseModel):
    """
    System health check response.

    Attributes
    ----------
    status : str
        Service status
    uptime : str
        Service uptime
    dataset_loaded : bool
        Dataset load status
    """

    status: str
    uptime: str
    dataset_loaded: bool


class MetadataResponse(BaseModel):
    """
    System metadata response.

    Attributes
    ----------
    version : str
        API version
    last_update : str
        Last update timestamp
    """

    version: str
    last_update: str
