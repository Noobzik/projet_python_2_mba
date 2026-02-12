"""
Routes pour l'administration système.

Ce module définit les endpoints API pour les métadonnées
et la supervision du service.
"""

from typing import Any, Dict
from fastapi import APIRouter

from banking_api.models.schemas import SystemHealth, SystemMetadata
from banking_api.services.system_service import system_service
from banking_api.services.data_loader import DataLoader

router: APIRouter = APIRouter(prefix="/api/system", tags=["Système"])


@router.get("/health", response_model=SystemHealth)
async def get_system_health() -> SystemHealth:
    """
    Vérifie l'état de santé de l'API.

    Returns
    -------
    SystemHealth
        État de santé du système incluant:
        - Statut (ok, degraded, error)
        - Temps de fonctionnement
        - État du chargement des données
        - Horodatage de la vérification
    """
    return system_service.get_health()


@router.get("/metadata", response_model=SystemMetadata)
async def get_system_metadata() -> SystemMetadata:
    """
    Informations sur la version du service et la date de dernière mise à jour.

    Returns
    -------
    SystemMetadata
        Métadonnées du système incluant:
        - Version de l'API
        - Date de dernière mise à jour
        - Nombre total de transactions
        - Source des données
    """
    return system_service.get_metadata()


@router.get("/debug/columns")
async def get_data_columns() -> Dict[str, Any]:
    """
    Debug endpoint: affiche les colonnes et types de données.

    Returns
    -------
    Dict[str, Any]
        Informations sur les colonnes disponibles dans les données
    """
    data_loader = DataLoader()
    df = data_loader.get_transactions()

    sample_data = df.head(3).to_dict(orient="records") if not df.empty else []

    return {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "total_rows": len(df),
        "sample_data": sample_data,
    }
