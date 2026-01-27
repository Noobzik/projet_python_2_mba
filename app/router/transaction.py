from app.services.transaction import *
from fastapi import APIRouter, Query, Body,HTTPException
from typing import Optional, Dict, Any

router = APIRouter(tags=["Transaction"])

@router.get("/api/transaction")
async def transaction_route(
    page: int = Query(1, description="Numéro de page"),
    limit: int = Query(5, description="Nombre de résultats par page"),
    tx_id: Optional[str] = Query(None, description="ID de la transaction"),
    tx_type: Optional[str] = Query(None, description="Type de la transaction"),
    amount: Optional[float] = Query(None, description="Montant minimum de la transaction"),
    isFraud: Optional[bool] = Query(None, description="Filtre fraude")
):
    
    # Appel dynamique de la fonction get_transactions
    result = get_transactions(
        page=page,
        limit=limit,
        type=tx_type,
        min_amount=amount,
        isFraud=isFraud
    )

    return {
        "success": True,
        "filters_applied": {
            "page": page,
            "limit": limit,
            "id": tx_id,
            "type": tx_type,
            "min_amount": amount,
            "isFraud": isFraud
        },
        "data": result
    }

@router.get("/api/transaction/{transaction_id}")
async def transaction_by_id_route(transaction_id: str):

    transaction = get_transaction_by_id(transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction avec ID '{transaction_id}' introuvable"
        )

    return {
        "success": True,
        "transaction": transaction
    }

@router.post("/api/transaction/search")
async def search_transactions_route(
    page: int = Body(1, description="Numéro de page"),
    limit: int = Body(10, description="Nombre de résultats par page"),
    tx_type: Optional[str] = Body(None, description="Type de la transaction"),
    isFraud: Optional[bool] = Body(None, description="Filtre fraude"),
    min_amount: Optional[float] = Body(None, description="Montant minimum"),
    max_amount: Optional[float] = Body(None, description="Montant maximum")
):
    """
    Recherche des transactions avec filtres dynamiques passés dans le body JSON.
    """

    # Construire le dictionnaire attendu par search_transactions
    filters = {
        "page": page,
        "limit": limit,
        "type": tx_type,
        "isFraud": isFraud,
        "min_amount": min_amount,
        "max_amount": max_amount
    }

    # Appel de la fonction
    result = search_transactions(filters)

    return {
        "success": True,
        "filters_applied": filters,
        "data": result
    }