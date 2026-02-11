"""Customer data models.

This module defines Pydantic models for customer-related data.
"""

from typing import List
from pydantic import BaseModel, Field


class CustomerProfile(BaseModel):
    """Customer profile with transaction summary.

    Parameters
    ----------
    id : int
        Customer identifier.
    transactions_count : int
        Number of transactions.
    avg_amount : float
        Average transaction amount.
    total_amount : float
        Total amount of transactions.
    fraudulent : bool
        Whether customer has fraudulent transactions.
    fraud_count : int
        Number of fraudulent transactions.
    """

    id: int
    transactions_count: int = Field(..., ge=0)
    avg_amount: float = Field(..., ge=0.0)
    total_amount: float = Field(..., ge=0.0)
    fraudulent: bool
    fraud_count: int = Field(..., ge=0)


class CustomerList(BaseModel):
    """Paginated list of customers.

    Parameters
    ----------
    page : int
        Current page number.
    limit : int
        Number of items per page.
    total : int
        Total number of customers.
    customers : List[int]
        List of customer IDs.
    """

    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    customers: List[int]


class TopCustomer(BaseModel):
    """Top customer by transaction volume.

    Parameters
    ----------
    id : str
        Customer identifier.
    total_amount : float
        Total transaction amount.
    transactions_count : int
        Number of transactions.
    """

    id: str
    total_amount: float = Field(..., ge=0.0)
    transactions_count: int = Field(..., ge=0)
