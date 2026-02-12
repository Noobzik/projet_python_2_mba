from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from app.services import customer_service

router = APIRouter()

@router.get("/", summary="Route 16: Lister les clients")
def list_customers(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100)
) -> Dict[str, Any]:
    """
    Liste paginée des utilisateurs (Infos démographiques).
    """
    return customer_service.get_all_customers(page, limit)

@router.get("/top", summary="Route 18: Top Clients")
def get_top_customers(n: int = Query(10, ge=1, le=100)) -> List[Dict[str, Any]]:
    """
    Retourne les N plus gros clients (par volume de transactions).
    Nécessite la fonction ajoutée dans le service juste avant.
    """
    # Attention: assure-toi d'avoir ajouté get_top_customers dans ton service !
    return customer_service.get_top_customers(n)

@router.get("/{client_id}", summary="Route 17: Profil Client 360")
def get_customer_details(client_id: int) -> Dict[str, Any]:
    """
    Retourne la fiche complète d'un client :
    - Données perso (Age, Revenu, Score Crédit)
    - Habitudes de dépenses (Total, Panier moyen, Fraude)
    """
    data = customer_service.get_customer_profile(client_id)
    if not data:
        raise HTTPException(status_code=404, detail="Client introuvable")
    return data