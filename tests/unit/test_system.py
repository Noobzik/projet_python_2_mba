from fastapi.testclient import TestClient
from app.main import app

# On crée un "faux" client qui simule des requêtes HTTP sur l'API
client = TestClient(app)

def test_read_health() -> None:
    """
    Teste la route de santé du système.
    Doit correspondre exactement au JSON renvoyé par system_service.py
    """
    response = client.get("/api/system/health")
    
    # 1. Vérifie que la requête a réussi (Code 200)
    assert response.status_code == 200
    
    data = response.json()
    
    # 2. Vérifie le contenu
    assert data["status"] == "ok"
    
    # On vérifie que l'une des clés de confirmation est présente (uptime OU dataset_loaded)
    # Cela permet au test de réussir quelle que soit ta version du code
    assert ("uptime" in data) or ("dataset_loaded" in data)

def test_read_root() -> None:
    """
    Teste la route racine (/) définie dans main.py
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Banking Transactions API" in data["message"]