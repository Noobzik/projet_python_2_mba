"""Routes des transactions pour l’API.

Ce module définit tous les endpoints liés aux transactions (Routes 1-8).
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from banking_api.config import DEFAULT_LIMIT, DEFAULT_PAGE, DEFAULT_RECENT_N
from banking_api.models.transaction import (TransactionListResponse,
                                            TransactionResponse,
                                            TransactionSearchRequest)
from banking_api.services.transactions_service import TransactionsService

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])
service = TransactionsService()


@router.get("", response_model=TransactionListResponse)
async def get_transactions(
    page: int = Query(DEFAULT_PAGE, ge=1, description="Numéro de page"),
    limit: int = Query(
        DEFAULT_LIMIT, ge=1, le=1000, description="Nombre d’éléments par page"
    ),
    type: Optional[str] = Query(None, description="Filtrer par type de transaction"),
    isFraud: Optional[int] = Query(
        None, ge=0, le=1, description="Filtrer par statut de fraude"
    ),
    min_amount: Optional[float] = Query(None, ge=0, description="Montant minimum"),
    max_amount: Optional[float] = Query(None, ge=0, description="Montant maximum"),
) -> TransactionListResponse:
    """Récupérer une liste paginée de transactions avec filtres optionnels."""
    return service.get_all_transactions(
        page=page,
        limit=limit,
        type_filter=type,
        is_fraud=isFraud,
        min_amount=min_amount,
        max_amount=max_amount,
    )


@router.post("/search", response_model=List[TransactionResponse])
async def search_transactions(
    request: TransactionSearchRequest,
) -> List[TransactionResponse]:
    """Rechercher des transactions selon plusieurs critères."""
    return service.search_transactions(request)


@router.get("/types", response_model=List[str])
async def get_transaction_types() -> List[str]:
    """Récupérer la liste des types de transactions disponibles."""
    return service.get_transaction_types()


@router.get("/recent", response_model=List[TransactionResponse])
async def get_recent_transactions(
    n: int = Query(
        DEFAULT_RECENT_N, ge=1, le=100, description="Nombre de transactions récentes"
    )
) -> List[TransactionResponse]:
    """Récupérer les N transactions les plus récentes."""
    return service.get_recent_transactions(n)


@router.get("/by-customer/{customer_id}", response_model=List[TransactionResponse])
async def get_transactions_by_customer(customer_id: str) -> List[TransactionResponse]:
    """Récupérer toutes les transactions initiées par un client spécifique."""
    return service.get_transactions_by_customer(customer_id)


@router.get("/to-customer/{customer_id}", response_model=List[TransactionResponse])
async def get_transactions_to_customer(customer_id: str) -> List[TransactionResponse]:
    """Récupérer toutes les transactions reçues par un client spécifique."""
    return service.get_transactions_to_customer(customer_id)


@router.get("/{id}", response_model=TransactionResponse)
async def get_transaction_by_id(id: str) -> TransactionResponse:
    """Récupérer les détails d’une transaction spécifique par identifiant."""
    transaction = service.get_transaction_by_id(id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {id} introuvable",
        )
    return transaction


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(id: str) -> None:
    """Supprimer une transaction (mode test uniquement)."""

    transaction = service.get_transaction_by_id(id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {id} introuvable",
        )

    service.delete_transaction(id)
