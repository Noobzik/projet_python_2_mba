"""
Routes pour la gestion des transactions.

Ce module définit les endpoints API pour la consultation,
le filtrage et la manipulation des transactions.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query

from banking_api.models.schemas import (
    Transaction,
    TransactionResponse,
    TransactionSearch,
)
from banking_api.services.transactions_service import transactions_service

router: APIRouter = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionResponse)
async def get_transactions(
    page: int = Query(1, ge=1, description="Numéro de page"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre par page"),
    use_chip: Optional[str] = Query(None, description="Type d'utilisation de carte"),
    has_errors: Optional[bool] = Query(
        None, description="Filtre fraude (transactions avec erreurs)"
    ),
    min_amount: Optional[float] = Query(None, ge=0, description="Montant minimum"),
    max_amount: Optional[float] = Query(None, ge=0, description="Montant maximum"),
) -> TransactionResponse:
    """
    Liste paginée des transactions avec filtres optionnels.

    Parameters
    ----------
    page : int
        Numéro de la page
    limit : int
        Nombre d'éléments par page
    use_chip : Optional[str]
        Filtre par type d'utilisation de carte
    has_errors : Optional[bool]
        Filtre par fraude (True = avec erreurs)
    min_amount : Optional[float]
        Montant minimum
    max_amount : Optional[float]
        Montant maximum

    Returns
    -------
    TransactionResponse
        Réponse paginée contenant les transactions
    """
    return transactions_service.get_all_transactions(
        page=page,
        limit=limit,
        use_chip=use_chip,
        has_errors=has_errors,
        min_amount=min_amount,
        max_amount=max_amount,
    )


@router.post("/search", response_model=TransactionResponse)
async def search_transactions(
    search_criteria: TransactionSearch,
) -> TransactionResponse:
    """
    Recherche multicritère de transactions.

    Parameters
    ----------
    search_criteria : TransactionSearch
        Critères de recherche (page, limit, use_chip, isFraud, amount_range, etc.)

    Returns
    -------
    TransactionResponse
        Résultats de la recherche paginés
    """
    page = search_criteria.page or 1
    limit = search_criteria.limit or 50
    return transactions_service.search_transactions(search_criteria, page, limit)


@router.get("/types", response_model=List[str])
async def get_transaction_types() -> List[str]:
    """
    Liste des types de transactions disponibles.

    Returns
    -------
    List[str]
        Liste des types de transactions uniques
    """
    return transactions_service.get_transaction_types()


@router.get("/recent", response_model=List[Transaction])
async def get_recent_transactions(
    n: int = Query(10, ge=1, le=100, description="Nombre de transactions")
) -> List[Transaction]:
    """
    Renvoie les N dernières transactions du dataset.

    Parameters
    ----------
    n : int
        Nombre de transactions à retourner (défaut: 10)

    Returns
    -------
    List[Transaction]
        Liste des dernières transactions
    """
    return transactions_service.get_recent_transactions(n)


@router.get("/{id}", response_model=Transaction)
async def get_transaction_by_id(
    id: int = Path(..., description="Identifiant de la transaction")
) -> Transaction:
    """
    Détails d'une transaction par son identifiant.

    Parameters
    ----------
    id : int
        Identifiant unique de la transaction

    Returns
    -------
    Transaction
        Détails de la transaction

    Raises
    ------
    HTTPException
        404 si la transaction n'est pas trouvée
    """
    transaction: Optional[Transaction] = transactions_service.get_transaction_by_id(id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    return transaction


@router.delete("/{id}")
async def delete_transaction(
    id: int = Path(..., description="Identifiant de la transaction")
) -> dict:
    """
    Supprime une transaction (mode test uniquement).

    Parameters
    ----------
    id : str
        Identifiant de la transaction à supprimer

    Returns
    -------
    dict
        Message de confirmation

    Raises
    ------
    HTTPException
        404 si la transaction n'est pas trouvée
    """
    success: bool = transactions_service.delete_transaction(id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    return {"message": f"Transaction {id} supprimée avec succès"}


@router.get("/by-customer/{customer_id}", response_model=List[Transaction])
async def get_transactions_by_customer(
    customer_id: int = Path(..., description="Identifiant du client")
) -> List[Transaction]:
    """
    Liste des transactions associées à un client (origine).

    Parameters
    ----------
    customer_id : str
        Identifiant du client

    Returns
    -------
    List[Transaction]
        Liste des transactions du client
    """
    return transactions_service.get_transactions_by_customer(
        customer_id, as_origin=True
    )


@router.get("/to-customer/{customer_id}", response_model=List[Transaction])
async def get_transactions_to_customer(
    customer_id: int = Path(..., description="Identifiant du client")
) -> List[Transaction]:
    """
    Liste des transactions reçues par un client (destination).

    Parameters
    ----------
    customer_id : str
        Identifiant du client

    Returns
    -------
    List[Transaction]
        Liste des transactions reçues
    """
    return transactions_service.get_transactions_by_customer(
        customer_id, as_origin=False
    )
