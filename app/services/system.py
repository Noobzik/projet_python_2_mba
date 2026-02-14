import time
from typing import Dict, Any

# Initialisation au démarrage de l'application
moment_depart = time.time()

# Simulation d'un DataFrame 
df = None 

def get_system_health() -> Dict[str, Any]:
    uptime_seconds = int(time.time() - moment_depart)
    hours, rem = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return {
        "status": "healthy",
        "uptime": f"{hours}h {minutes}m {seconds}s",
        "dataset_ready": df is not None
    }
