"""
Tests unitaires pour les routes système.

Ce module teste tous les endpoints liés au système.
"""

from fastapi.testclient import TestClient

from banking_api.main import app

client: TestClient = TestClient(app)


class TestSystemRoutes:
    """Tests pour les routes système."""

    def test_get_system_health(self) -> None:
        """Test de récupération de l'état de santé."""
        response = client.get("/api/system/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "uptime" in data
        assert "dataset_loaded" in data
        assert "timestamp" in data
        assert data["status"] in ["ok", "degraded", "error"]
        assert isinstance(data["dataset_loaded"], bool)

    def test_get_system_metadata(self) -> None:
        """Test de récupération des métadonnées."""
        response = client.get("/api/system/metadata")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "last_update" in data
        assert "total_transactions" in data
        assert "data_source" in data
        assert data["version"] == "1.0.0"
        assert isinstance(data["total_transactions"], int)

    def test_root_endpoint(self) -> None:
        """Test de l'endpoint racine."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "documentation" in data
