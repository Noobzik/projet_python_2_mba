"""Customer routes.

This module defines API endpoints for customer operations.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query
from ..models.customer import CustomerProfile, CustomerList, TopCustomer
from ..services.customer_service import CustomerService

router = APIRouter(prefix="/api/customers", tags=["customers"])
service = CustomerService()


@router.get("", response_model=CustomerList)
def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page")
) -> CustomerList:
    """Get paginated list of customers.

    Parameters
    ----------
    page : int
        Page number (default: 1).
    limit : int
        Items per page (default: 50, max: 100).

    Returns
    -------
    CustomerList
        Paginated list of customer IDs.
    """
    return service.get_customers(page, limit)


@router.get("/top", response_model=List[TopCustomer])
def get_top_customers(
    n: int = Query(10, ge=1, le=100, description="Number of top customers")
) -> List[TopCustomer]:
    """Get top customers by transaction volume.

    Parameters
    ----------
    n : int
        Number of top customers to retrieve (default: 10, max: 100).

    Returns
    -------
    List[TopCustomer]
        List of top customers sorted by total transaction amount.
    """
    return service.get_top_customers(n)


@router.get("/{customer_id}", response_model=CustomerProfile)
def get_customer_profile(customer_id: int) -> CustomerProfile:
    """Get customer profile with transaction summary.

    Parameters
    ----------
    customer_id : int
        Customer identifier.

    Returns
    -------
    CustomerProfile
        Customer profile including transaction counts,
        amounts, and fraud information.

    Raises
    ------
    HTTPException
        404 if customer not found.
    """
    try:
        return service.get_customer_profile(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
