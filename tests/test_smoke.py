from fastapi.testclient import TestClient

from banking_api.main import create_app


def test_smoke_docs_available() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/docs")
    assert r.status_code == 200
