"""
Customers Router.

Exposes endpoints 16–18 for customer portfolio exploration.
"""

from fastapi import APIRouter, HTTPException, Query

from banking_api.models.schemas import (
    CustomerProfile,
    CustomerSummary,
    TopCustomer,
)
from banking_api.services import customer_service as svc

router: APIRouter = APIRouter()


@router.get("", response_model=list[CustomerSummary], summary="List customers")
def list_customers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=500),
) -> list[CustomerSummary]:
    """Return a paginated list of unique originating customers.

    Parameters
    ----------
    page : int
        Page number (1-indexed).
    limit : int
        Records per page (max 500).

    Returns
    -------
    list[CustomerSummary]
        Customer IDs with their transaction counts.
    """
    return svc.list_customers(page=page, limit=limit)


@router.get(
    "/top",
    response_model=list[TopCustomer],
    summary="Top customers by volume",
)
def get_top_customers(
    n: int = Query(default=10, ge=1, le=100, description="Number of top customers"),
) -> list[TopCustomer]:
    """Return the top *n* customers ranked by total transaction volume.

    Parameters
    ----------
    n : int
        Number of customers to return (default 10).

    Returns
    -------
    list[TopCustomer]
        Customers sorted by descending total transaction volume.
    """
    return svc.get_top_customers(n=n)


@router.get(
    "/{customer_id}",
    response_model=CustomerProfile,
    summary="Customer profile",
)
def get_customer(customer_id: str) -> CustomerProfile:
    """Return a synthetic profile for a single customer.

    Parameters
    ----------
    customer_id : str
        ``nameOrig`` identifier of the customer.

    Returns
    -------
    CustomerProfile
        Transaction count, average amount and fraud flag.

    Raises
    ------
    HTTPException
        404 if the customer is not found.
    """
    profile = svc.get_customer_profile(customer_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return profile
