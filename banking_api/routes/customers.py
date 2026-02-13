"""Routes client pour l’API.

Ce module définit tous les endpoints liés aux clients (Routes 16-18).
"""

from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from banking_api.config import DEFAULT_LIMIT, DEFAULT_PAGE, DEFAULT_TOP_N
from banking_api.models.schemas import (CustomerListResponse, CustomerProfile,
                                        TopCustomer)
from banking_api.services.customer_service import CustomerService

router = APIRouter(prefix="/api/customers", tags=["Customers"])
service = CustomerService()


@router.get("", response_model=CustomerListResponse)
async def get_customers(
    page: int = Query(DEFAULT_PAGE, ge=1, description="Numéro de page"),
    limit: int = Query(
        DEFAULT_LIMIT, ge=1, le=1000, description="Nombre d’éléments par page"
    ),
) -> CustomerListResponse:
    """Récupérer une liste paginée des clients."""
    return service.get_all_customers(page=page, limit=limit)


@router.get("/top", response_model=List[TopCustomer])
async def get_top_customers(
    n: int = Query(
        DEFAULT_TOP_N, ge=1, le=100, description="Nombre de meilleurs clients"
    )
) -> List[TopCustomer]:
    """Récupérer les N meilleurs clients selon le volume de transactions."""
    return service.get_top_customers(n)


@router.get("/{customer_id}", response_model=CustomerProfile)
async def get_customer_profile(customer_id: str) -> CustomerProfile:
    """Récupérer le profil détaillé d’un client spécifique."""
    profile = service.get_customer_profile(customer_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {customer_id} introuvable",
        )
    return profile
