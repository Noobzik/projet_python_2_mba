"""
Tests unitaires pour les routes de statistiques.

Ce module teste tous les endpoints liés aux statistiques.
"""

from fastapi.testclient import TestClient

from banking_api.main import app

client: TestClient = TestClient(app)


class TestStatisticsRoutes:
    """Tests pour les routes de statistiques."""

    def test_get_stats_overview(self) -> None:
        """Test de récupération de la vue d'ensemble."""
        response = client.get("/api/stats/overview")
        assert response.status_code == 200
        data = response.json()
        assert "total_transactions" in data
        assert "fraud_rate" in data
        assert "avg_amount" in data
        assert "most_common_type" in data
        assert data["total_transactions"] > 0

    def test_get_amount_distribution(self) -> None:
        """Test de récupération de la distribution des montants."""
        response = client.get("/api/stats/amount-distribution")
        assert response.status_code == 200
        data = response.json()
        assert "bins" in data
        assert "counts" in data
        assert isinstance(data["bins"], list)
        assert isinstance(data["counts"], list)
        assert len(data["bins"]) == len(data["counts"])

    def test_get_stats_by_type(self) -> None:
        """Test de récupération des stats par type."""
        response = client.get("/api/stats/by-type")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Vérifier la structure d'un élément
        if data:
            assert "type" in data[0]
            assert "count" in data[0]
            assert "avg_amount" in data[0]
            assert "total_amount" in data[0]

    def test_get_daily_stats(self) -> None:
        """Test de récupération des stats quotidiennes."""
        response = client.get("/api/stats/daily")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Vérifier la structure
        if data:
            assert "step" in data[0]
            assert "count" in data[0]
            assert "avg_amount" in data[0]
            assert "total_amount" in data[0]
