from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_system_health():
    r = client.get("/api/system/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "uptime" in body


def test_system_metadata():
    r = client.get("/api/system/metadata")
    assert r.status_code == 200
    body = r.json()
    assert "version" in body
