"""Routes système pour l’API.

Ce module définit tous les endpoints liés au système (Routes 19-20).
"""

from fastapi import APIRouter

from banking_api.models.schemas import HealthResponse, MetadataResponse
from banking_api.services.system_service import SystemService

router = APIRouter(prefix="/api/system", tags=["System"])
service = SystemService()


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Vérifier l’état de santé de l’API.

    Returns
    -------
    HealthResponse
        Informations de contrôle incluant :
        - Statut du service
        - Temps de fonctionnement
        - État de chargement du dataset
        - Nombre total d’enregistrements
    """
    return service.get_health()


@router.get("/metadata", response_model=MetadataResponse)
async def get_metadata() -> MetadataResponse:
    """Récupérer les informations de métadonnées de l’API.

    Returns
    -------
    MetadataResponse
        Métadonnées système incluant :
        - Version de l’API
        - Horodatage de la dernière mise à jour
        - Nombre total d’endpoints
        - Informations sur le dataset
    """
    return service.get_metadata()
