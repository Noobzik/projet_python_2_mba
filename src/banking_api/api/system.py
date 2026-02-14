from datetime import datetime
from fastapi import APIRouter
from banking_api.services.dataset_loader import get_status

router = APIRouter()

# ⏱️ On capture l'heure exacte au démarrage du serveur
START_TIME = datetime.now()

@router.get("/health")
def health_check():
    """
    Vérifie l'état de santé de l'API.
    Retourne l'uptime réel et l'état du dataset.
    """
    # Calcul du temps écoulé
    now = datetime.now()
    uptime_duration = now - START_TIME
    
    # On convertit en texte propre (ex: "0:12:45") en enlevant les millisecondes
    uptime_str = str(uptime_duration).split('.')[0]

    status = get_status()
    
    return {
        "status": "ok", 
        "uptime": uptime_str,  # <--- C'est ici que la magie opère
        "dataset_loaded": status.loaded,
        "rows_in_memory": status.rows
    }

@router.get("/metadata")
def get_metadata():
    """
    Informations sur la version du service (Route 20).
    """
    return {
        "version": "2.1.0",
        "last_update": datetime.now().strftime("%Y-%m-%d"),
        "author": "Group 2",
        "dataset_source": "Kaggle (Universal Adapter)"
    }