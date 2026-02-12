"""
Customers router for Banking Transactions API.

This module defines the API endpoints for customer portfolio exploration.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.schemas import (
    Customer,
    PaginatedCustomersResponse,
    TopCustomer,
)
from app.services.customer_service import (
    get_customers,
    get_customer_profile,
    get_top_customers,
)

router = APIRouter(tags=["Customers"])


# 16️⃣ GET /api/customers
@router.get("/customers", response_model=PaginatedCustomersResponse)
def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Items per page"),
) -> PaginatedCustomersResponse:
    """
    Get paginated list of customers.

    Parameters
    ----------
    page : int
        Page number (starting from 1)
    limit : int
        Number of items per page (max 1000)

    Returns
    -------
    PaginatedCustomersResponse
        Paginated list of customer IDs
    """
    return get_customers(page=page, limit=limit)


# 18️⃣ GET /api/customers/top - DÉPLACÉ AVANT /{customer_id}
@router.get("/customers/top", response_model=List[TopCustomer])
def get_top(
    n: int = Query(10, ge=1, le=100, description="Number of top customers")
) -> List[TopCustomer]:
    """
    Get top customers ranked by transaction volume.

    Parameters
    ----------
    n : int
        Number of top customers to return (default: 10, max: 100)

    Returns
    -------
    List[TopCustomer]
        Top customers with:
        - Customer ID
        - Total transaction amount
        - Transaction count
    """
    return get_top_customers(n)


# 17️⃣ GET /api/customers/{customer_id} - DÉPLACÉ APRÈS /top
@router.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str) -> Customer:
    """
    Get comprehensive customer profile.

    Parameters
    ----------
    customer_id : str
        Customer unique identifier

    Returns
    -------
    Customer
        Customer profile including:
        - Customer ID
        - Number of transactions
        - Average transaction amount
        - Total transaction amount
        - Fraud involvement flag

    Raises
    ------
    HTTPException
        404 if customer not found
    """
    profile = get_customer_profile(customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Customer not found")
    return profile