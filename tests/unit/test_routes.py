from fastapi.testclient import TestClient
from app.main import app

# On instancie le client de test
client = TestClient(app)

# ==========================================
# 1. TESTS TRANSACTIONS (8 Tests)
# ==========================================

def test_03_list_transactions():
    """Liste paginée des transactions (Route 1)."""
    response = client.get("/api/transactions/?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert len(data["transactions"]) <= 5

def test_04_transaction_types():
    """Liste des types disponibles (Route 4)."""
    response = client.get("/api/transactions/types")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_05_recent_transactions():
    """Transactions récentes (Route 5)."""
    response = client.get("/api/transactions/recent?limit=3")
    assert response.status_code == 200
    assert len(response.json()) <= 3

def test_06_search_transactions():
    """Recherche multicritère (Route 3)."""
    payload = {"min_amount": 10, "max_amount": 1000}
    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_07_transaction_detail():
    """Détail d'une transaction (Route 2)."""
    # Etape 1 : On récupère une transaction réelle pour avoir un ID valide
    list_resp = client.get("/api/transactions/?limit=1")
    txs = list_resp.json().get("transactions", [])
    
    if txs:
        tx_id = txs[0]["id"]
        # Etape 2 : On teste le détail de cet ID
        response = client.get(f"/api/transactions/{tx_id}")
        assert response.status_code == 200
        assert response.json()["id"] == tx_id

def test_08_delete_transaction():
    """Suppression simulée (Route 6)."""
    response = client.delete("/api/transactions/123456")
    # On accepte 200 (supprimé) ou 404 (pas trouvé), tant que ça ne plante pas (500)
    assert response.status_code in [200, 404]

def test_09_transactions_by_customer():
    """Historique client (Route 7)."""
    response = client.get("/api/transactions/by-customer/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_10_transactions_to_merchant():
    """Historique marchand (Route 8)."""
    response = client.get("/api/transactions/to-customer/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ==========================================
# 2. TESTS STATISTIQUES (5 Tests)
# ==========================================

def test_11_stats_global():
    """KPI Globaux (Route 9)."""
    response = client.get("/api/stats/global")
    assert response.status_code == 200
    data = response.json()
    assert "volume" in data
    assert "fraud" in data

def test_12_stats_by_type():
    """Stats par type (Route 11)."""
    response = client.get("/api/stats/by-type")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_13_amount_distribution():
    """Histogramme (Route 10)."""
    response = client.get("/api/stats/amount-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "bins" in data
    assert "counts" in data

def test_14_stats_daily():
    """Volume journalier (Route 12)."""
    response = client.get("/api/stats/daily")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_15_top_sectors():
    """Top secteurs (Route Bonus)."""
    response = client.get("/api/stats/top-sectors")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ==========================================
# 3. TESTS FRAUDE (4 Tests)
# ==========================================

def test_16_fraud_summary():
    """Dashboard Fraude (Route 13)."""
    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "total_cases" in data["summary"]

def test_17_fraud_highest():
    """Top fraudes (Route Bonus)."""
    response = client.get("/api/fraud/highest")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_18_fraud_by_type():
    """Fraude par type (Route 14)."""
    response = client.get("/api/fraud/by-type")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_19_fraud_prediction():
    """Scoring IA (Route 15)."""
    payload = {
        "type": "Online Transaction",
        "amount": 999999,
        "oldbalanceOrg": 500,
        "newbalanceOrig": 0
    }
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "isFraud" in data
    assert data["isFraud"] is True

# ==========================================
# 4. TESTS CLIENTS (3 Tests)
# ==========================================

def test_20_list_customers():
    """Liste clients (Route 16)."""
    response = client.get("/api/customers/?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "customers" in data

def test_21_top_customers():
    """Top clients (Route 18)."""
    response = client.get("/api/customers/top?n=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_22_customer_profile():
    """Profil client (Route 17)."""
    response = client.get("/api/customers/1")
    # On accepte 200 (trouvé) ou 404 (pas trouvé), l'important est que l'API réponde
    assert response.status_code in [200, 404]