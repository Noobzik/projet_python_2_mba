"""
Tests unitaires pour les routes de clients.

Ce module teste tous les endpoints liés aux clients.
"""

from fastapi.testclient import TestClient

from banking_api.main import app

client: TestClient = TestClient(app)


class TestCustomersRoutes:
    """Tests pour les routes de clients."""

    def test_get_customers(self) -> None:
        """Test de récupération de la liste des clients."""
        response = client.get("/api/customers?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert "page" in data
        assert "total" in data
        assert isinstance(data["customers"], list)
        assert data["page"] == 1

    def test_get_customer_profile(self) -> None:
        """Test de récupération d'un profil client."""
        # D'abord, récupérer un client valide
        list_response = client.get("/api/customers?limit=1")
        customers = list_response.json()["customers"]

        if customers:
            customer_id = customers[0]
            response = client.get(f"/api/customers/{customer_id}")
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "transactions_count" in data
            assert "avg_amount" in data
            assert "total_amount" in data
            assert "fraudulent" in data
            assert data["id"] == customer_id

    def test_get_customer_profile_invalid(self) -> None:
        """Test avec un client invalide."""
        # Utiliser un ID client inexistant
        response = client.get("/api/customers/99999999")
        assert response.status_code == 404

    def test_get_top_customers_by_volume(self) -> None:
        """Test de récupération du top clients par volume."""
        response = client.get("/api/customers/top?n=5&by=volume")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        # Vérifier le tri par volume
        if len(data) > 1:
            assert data[0]["total_amount"] >= data[1]["total_amount"]

    def test_get_top_customers_by_count(self) -> None:
        """Test de récupération du top clients par nombre."""
        response = client.get("/api/customers/top?n=5&by=count")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        # Vérifier le tri par nombre
        if len(data) > 1:
            assert data[0]["transactions_count"] >= data[1]["transactions_count"]
