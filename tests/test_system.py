
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import time
import pandas as pd
import app.services.system as system_module

# Importer la route et les fonctions
from app.router.system import router_system, get_system_health, get_metadata
from app.services.system import get_system_health, df, moment_depart

#test app.router.system
# Créer une instance FastAPI pour inclure le router
app = FastAPI()
app.include_router(router_system)

client = TestClient(app)

# Tests des fonctions

def test_get_system_health_returns_expected_keys():
    health = get_system_health()
    assert isinstance(health, dict)
    assert health["status"] == "healthy"
    assert "uptime" in health
    assert "h" in health["uptime"]  # Vérifie que le format inclut heures
    assert "dataset_ready" in health
    assert health["dataset_ready"] is False  # Comme df=None

def test_get_metadata_returns_expected_values():
    meta = get_metadata()
    assert meta["version"] == "1.0.0"
    assert meta["last_update"] == "2026-02-03"
    assert meta["author"] == "CFMM"

# Tests des routes FastAPI

def test_health_route():
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime" in data
    assert data["dataset_ready"] is False

def test_metadata_route():
    response = client.get("/api/system/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["last_update"] == "2026-02-03"
    assert data["author"] == "CFMM"


# Test que l'uptime augmente avec le temps

def test_system_health_uptime_increases():
    health1 = get_system_health()
    time.sleep(1)  # attendre 1 seconde
    health2 = get_system_health()
    # Extraire le nombre de secondes
    sec1 = sum(int(x[:-1]) * factor for x, factor in zip(health1["uptime"].split(), [3600, 60, 1]))
    sec2 = sum(int(x[:-1]) * factor for x, factor in zip(health2["uptime"].split(), [3600, 60, 1]))
    assert sec2 >= sec1 + 1

#test app.services.system

# Fonction utilitaire pour parser "0h 0m 0s" en secondes

def parse_uptime(uptime_str: str) -> int:
    # Convertit 'Xh Ym Zs' en secondes totales
    hours = minutes = seconds = 0
    parts = uptime_str.split()
    for part in parts:
        if part.endswith("h"):
            hours = int(part[:-1])
        elif part.endswith("m"):
            minutes = int(part[:-1])
        elif part.endswith("s"):
            seconds = int(part[:-1])
    return hours*3600 + minutes*60 + seconds

# Test 1 : Structure de retour

def test_get_system_health_returns_expected_keys():
    result = system_module.get_system_health()
    assert isinstance(result, dict)
    assert "status" in result
    assert "uptime" in result
    assert "dataset_ready" in result
    assert result["status"] == "healthy"
    # df initial est None
    assert result["dataset_ready"] is False
    # uptime doit contenir h, m, s
    assert "h" in result["uptime"]
    assert "m" in result["uptime"]
    assert "s" in result["uptime"]

# Test 2 : uptime augmente avec le temps

def test_get_system_health_uptime_increases():
    result1 = system_module.get_system_health()
    time.sleep(1)
    result2 = system_module.get_system_health()
    
    sec1 = parse_uptime(result1["uptime"])
    sec2 = parse_uptime(result2["uptime"])
    
    assert sec2 >= sec1 + 1  # au moins 1 seconde de différence


# Test 3 : dataset_ready True quand df chargé

def test_get_system_health_dataset_ready(monkeypatch):
    # Simule un DataFrame chargé
    monkeypatch.setattr(system_module, "df", pd.DataFrame({"A": [1,2]}))
    result = system_module.get_system_health()
    
    assert result["dataset_ready"] is True
    assert result["status"] == "healthy"
    assert "h" in result["uptime"]
