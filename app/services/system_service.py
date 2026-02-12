from datetime import datetime
from typing import Dict, Any
from app.core.config import settings

# On initialise l'heure de démarrage ici, au moment où le fichier est chargé par Python
START_TIME = datetime.now()

def get_health_status() -> Dict[str, Any]:
    """
    [cite_start]Calcule l'état de santé du système [cite: 130-131].
    """
    # Calcul de la durée de fonctionnement
    uptime = datetime.now() - START_TIME
    
    # Vérification si le dataset est bien en mémoire
    df = settings.get_df()
    is_loaded = df is not None and not df.empty

    return {
        "status": "ok",  # Doit correspondre à ce que ton test attend
        "uptime": str(uptime).split('.')[0],  # Enlève les microsecondes pour faire propre (ex: "2:15:30")
        "dataset_loaded": is_loaded,
        "api_version": settings.VERSION if hasattr(settings, "VERSION") else "1.0.0"
    }

def get_metadata() -> Dict[str, str]:
    """
    Renvoie les métadonnées (si ton routeur appelle ce service pour metadata aussi)
    """
    return {
        "version": "1.0.0",
        "last_update": "2025-12-20T22:00:00Z"
    }