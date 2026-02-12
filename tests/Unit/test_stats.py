from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_stats_overview():
    r = client.get("/api/stats/overview")
    assert r.status_code == 200
    body = r.json()
    assert "total_transactions" in body
    assert "fraud_rate" in body


def test_amount_distribution():
    r = client.get("/api/stats/amount-distribution")
    assert r.status_code == 200
    assert "bins" in r.json()
    assert "counts" in r.json()


def test_stats_by_type():
    r = client.get("/api/stats/by-type")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_stats_daily():
    r = client.get("/api/stats/daily")
    assert r.status_code == 200
