"""
Routes pour la gestion des clients.

Ce module définit les endpoints API pour l'exploration
des profils clients.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query

from banking_api.models.schemas import Customer, CustomerListResponse
from banking_api.services.customer_service import customer_service

router: APIRouter = APIRouter(prefix="/api/customers", tags=["Clients"])


@router.get("", response_model=CustomerListResponse)
async def get_customers(
    page: int = Query(1, ge=1, description="Numéro de page"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre par page"),
) -> CustomerListResponse:
    """
    Liste paginée des clients.

    Parameters
    ----------
    page : int
        Numéro de la page
    limit : int
        Nombre d'éléments par page

    Returns
    -------
    CustomerListResponse
        Réponse paginée contenant les identifiants clients
    """
    return customer_service.get_all_customers(page=page, limit=limit)


@router.get("/top", response_model=List[Customer])
async def get_top_customers(
    n: int = Query(10, ge=1, le=100, description="Nombre de clients"),
    by: str = Query("volume", pattern="^(volume|count)$", description="Critère de tri"),
) -> List[Customer]:
    """
    Top clients classés par volume total de transactions ou nombre.

    Parameters
    ----------
    n : int
        Nombre de clients à retourner (défaut: 10)
    by : str
        Critère de classement: 'volume' ou 'count' (défaut: 'volume')

    Returns
    -------
    List[Customer]
        Liste des meilleurs clients triés selon le critère choisi
    """
    return customer_service.get_top_customers(n=n, by=by)


@router.get("/{customer_id}", response_model=Customer)
async def get_customer_profile(
    customer_id: int = Path(..., description="Identifiant du client")
) -> Customer:
    """
    Profil client synthétique.

    Parameters
    ----------
    customer_id : int
        Identifiant unique du client

    Returns
    -------
    Customer
        Profil du client incluant:
        - Nombre de transactions
        - Montant moyen des transactions
        - Montant total
        - Indicateur de fraude

    Raises
    ------
    HTTPException
        404 si le client n'est pas trouvé
    """
    customer: Optional[Customer] = customer_service.get_customer_profile(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return customer
