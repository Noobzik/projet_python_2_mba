from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_customers():
    r = client.get("/api/customers")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)  # ✅ C'est un dict
    assert "customers" in data
    assert isinstance(data["customers"], list)  # ✅ La liste est dans 'customers'


def test_customer_profile_not_found():
    r = client.get("/api/customers/UNKNOWN_ID")
    assert r.status_code == 404


def test_top_customers():
    r = client.get("/api/customers/top?n=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
