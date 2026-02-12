from fastapi import APIRouter
from app.services import system_service 
from app.core.config import settings
from typing import Dict, Any

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Vérifie l'état de santé de l'API [cite: 130-131].""" 
    # Mypy sera content car get_health_status() est maintenant bien typé
    return system_service.get_health_status()

@router.get("/metadata")
async def get_metadata() -> Dict[str, str]:
    """Informations sur la version du service [cite: 134-135].""" 
    return {
        "version": settings.VERSION,
        "last_update": "2025-12-20T22:00:00Z"
    }