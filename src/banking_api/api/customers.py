from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from banking_api.models.customer import CustomerProfileOut, TopCustomersOut
from banking_api.services.customers_service import customer_profile, list_customers, top_customers

router = APIRouter()


@router.get("/customers", response_model=dict)
def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> dict:
    try:
        customers = list_customers(page=page, limit=limit)
        return {"page": page, "customers": [c.model_dump() for c in customers]}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/customers/top", response_model=TopCustomersOut)
def get_top_customers(n: int = Query(10, ge=1, le=100)) -> TopCustomersOut:
    try:
        return top_customers(n=n)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/customers/{id}", response_model=CustomerProfileOut)
def get_customer(id: str) -> CustomerProfileOut:
    try:
        return customer_profile(id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
