from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.services import transactions_service

router = APIRouter()

# Modèle simple pour la recherche
class SearchCriteria(BaseModel):
    type: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    isFraud: Optional[int] = None

# --- ROUTE 1 : LISTE PAGINÉE ---
@router.get("/", summary="Route 1: Liste paginée")
async def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    type: Optional[str] = None
) -> Dict[str, Any]:
    """Liste paginée des transactions."""
    return transactions_service.get_paginated_transactions(page, limit, type)

# --- ROUTE 4 : TYPES DE TRANSACTIONS ---
@router.get("/types", summary="Route 4: Types disponibles")
async def get_transaction_types() -> List[str]:
    """Retourne la liste des types de transactions (ex: Online, Swipe)."""
    return transactions_service.get_transaction_types()

# --- ROUTE 5 : RÉCENTES ---
@router.get("/recent", summary="Route 5: Transactions récentes")
async def get_recent_transactions(limit: int = Query(10, le=50)) -> List[Dict[str, Any]]:
    """Retourne les N dernières transactions enregistrées."""
    return transactions_service.get_recent_transactions(limit)

# --- ROUTE 3 : RECHERCHE AVANCÉE (CORRECTION ICI) ---
@router.post("/search", summary="Route 3: Recherche multicritère")
async def search_transactions(criteria: SearchCriteria) -> List[Dict[str, Any]]:
    """Recherche par montant, type ou statut de fraude."""
    # CORRECTION : .dict() est déprécié, on utilise .model_dump() pour Pydantic V2
    return transactions_service.search_transactions(criteria.model_dump(exclude_none=True))

# --- ROUTE 7 : PAR CLIENT (SOURCE) ---
@router.get("/by-customer/{client_id}", summary="Route 7: Historique Client")
async def get_transactions_by_customer(client_id: int) -> List[Dict[str, Any]]:
    """Toutes les transactions effectuées par un client spécifique."""
    return transactions_service.get_transactions_by_customer(client_id)

# --- ROUTE 8 : PAR CLIENT (DESTINATION) ---
@router.get("/to-customer/{merchant_id}", summary="Route 8: Historique Marchand")
async def get_transactions_to_merchant(merchant_id: int) -> List[Dict[str, Any]]:
    """Transactions reçues par un marchand (destination)."""
    return transactions_service.get_transactions_to_merchant(merchant_id)

# --- ROUTE 2 : DÉTAIL ---
@router.get("/{tx_id}", summary="Route 2: Détail transaction")
async def get_transaction_details(tx_id: int) -> Dict[str, Any]:
    """Détails complets d'une transaction par son ID."""
    tx = transactions_service.get_transaction_by_id(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return tx

# --- ROUTE 6 : SUPPRESSION ---
@router.delete("/{tx_id}", summary="Route 6: Supprimer (Simulé)")
async def delete_transaction(tx_id: int) -> Dict[str, str]:
    """Simule la suppression d'une transaction."""
    success = transactions_service.delete_transaction(tx_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return {"status": "deleted", "id": str(tx_id), "message": "Transaction supprimée (simulation)"}