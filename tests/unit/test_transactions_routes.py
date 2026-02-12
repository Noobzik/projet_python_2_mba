"""
Tests unitaires pour les routes de transactions.

Ce module teste tous les endpoints liés aux transactions.
"""

from fastapi.testclient import TestClient

from banking_api.main import app

client: TestClient = TestClient(app)


class TestTransactionsRoutes:
    """Tests pour les routes de transactions."""

    def test_get_transactions(self) -> None:
        """Test de récupération de la liste des transactions."""
        response = client.get("/api/transactions?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "page" in data
        assert "total" in data
        assert data["page"] == 1

    def test_get_transactions_with_filters(self) -> None:
        """Test de récupération avec filtres."""
        response = client.get("/api/transactions?has_errors=true&min_amount=1000")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data

    def test_get_transaction_by_id(self) -> None:
        """Test de récupération d'une transaction par ID."""
        # D'abord, récupérer une transaction
        list_response = client.get("/api/transactions?limit=1")
        transactions = list_response.json()["transactions"]

        if transactions:
            transaction_id = transactions[0]["id"]
            response = client.get(f"/api/transactions/{transaction_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == transaction_id

    def test_get_transaction_by_invalid_id(self) -> None:
        """Test avec un ID invalide."""
        response = client.get("/api/transactions/999999999")
        assert response.status_code == 404

    def test_search_transactions(self) -> None:
        """Test de recherche de transactions."""
        search_data = {"use_chip": "Chip Transaction", "amount_range": [10, 100]}
        response = client.post("/api/transactions/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data

    def test_get_transaction_types(self) -> None:
        """Test de récupération des types de transactions."""
        response = client.get("/api/transactions/types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_recent_transactions(self) -> None:
        """Test de récupération des transactions récentes."""
        response = client.get("/api/transactions/recent?n=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_transactions_by_customer(self) -> None:
        """Test de récupération par client (origine)."""
        # Récupérer un client valide
        list_response = client.get("/api/transactions?limit=1")
        transactions = list_response.json()["transactions"]

        if transactions:
            customer_id = transactions[0]["client_id"]
            response = client.get(f"/api/transactions/by-customer/{customer_id}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_get_transactions_to_customer(self) -> None:
        """Test de récupération par client (destination)."""
        list_response = client.get("/api/transactions?limit=1")
        transactions = list_response.json()["transactions"]

        if transactions:
            customer_id = transactions[0]["client_id"]
            response = client.get(f"/api/transactions/to-customer/{customer_id}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_delete_transaction(self) -> None:
        """Test de suppression de transaction."""
        # Créer un ID de test
        response = client.delete("/api/transactions/999999999")
        # Peut retourner 404 si non trouvé, c'est normal
        assert response.status_code in [200, 404]
