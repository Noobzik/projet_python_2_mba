"""Tests pour les routes de l'API."""


class TestSystemRoutes:
    """Tests pour les routes système."""

    def test_health_endpoint(self, client):
        """Test : endpoint de santé fonctionne."""
        response = client.get("/api/system/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "dataset_loaded" in data

    def test_metadata_endpoint(self, client):
        """Test : endpoint de métadonnées fonctionne."""
        response = client.get("/api/system/metadata")

        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "last_update" in data


class TestFraudRoutes:
    """Tests pour les routes de fraude."""

    def test_fraud_summary_endpoint(self, client):
        """Test : GET /api/fraud/summary."""
        response = client.get("/api/fraud/summary")

        assert response.status_code == 200
        data = response.json()

        # Vérifier la structure
        assert "total_frauds" in data
        assert "flagged" in data
        assert "precision" in data
        assert "recall" in data

    def test_fraud_by_type_endpoint(self, client):
        """Test : GET /api/fraud/by-type."""
        response = client.get("/api/fraud/by-type")

        assert response.status_code == 200
        data = response.json()

        # Devrait retourner une liste
        assert isinstance(data, list)
        assert len(data) > 0

    def test_fraud_predict_endpoint_high_amount(self, client, sample_fraud_data):
        """Test : POST /api/fraud/predict avec montant élevé."""
        response = client.post("/api/fraud/predict", json=sample_fraud_data)

        assert response.status_code == 200
        data = response.json()

        assert "isFraud" in data
        assert "probability" in data
        assert "reasons" in data
        assert data["isFraud"] is True

    def test_fraud_predict_endpoint_normal(self, client, sample_normal_transaction):
        """Test : POST /api/fraud/predict avec transaction normale."""
        response = client.post("/api/fraud/predict", json=sample_normal_transaction)

        assert response.status_code == 200
        data = response.json()

        assert data["isFraud"] is False
        assert data["probability"] < 0.5


class TestStatsRoutes:
    """Tests pour les routes de statistiques."""

    def test_stats_overview_endpoint(self, client):
        """Test : GET /api/stats/overview."""
        response = client.get("/api/stats/overview")

        assert response.status_code == 200
        data = response.json()

        # Vérifier la structure
        assert "total_transactions" in data
        assert "fraud_rate" in data
        assert "avg_amount" in data
        assert "most_common_type" in data

        # Vérifier les types
        assert isinstance(data["total_transactions"], int)
        assert isinstance(data["fraud_rate"], float)

    def test_stats_by_type_endpoint(self, client):
        """Test : GET /api/stats/by-type."""
        response = client.get("/api/stats/by-type")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        # Vérifier la structure du premier élément
        first = data[0]
        assert "type" in first
        assert "count" in first
        assert "avg_amount" in first


class TestTransactionRoutes:
    """Tests pour les routes de transactions."""

    def test_transactions_pagination(self, client):
        """Test : GET /api/transactions avec pagination."""
        response = client.get("/api/transactions?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()

        # Vérifier la pagination
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert "transactions" in data

        # Vérifier que la limite est respectée
        assert len(data["transactions"]) <= 10

    def test_transaction_types_endpoint(self, client):
        """Test : GET /api/transactions/types."""
        response = client.get("/api/transactions/types")

        assert response.status_code == 200
        data = response.json()

        assert "types" in data
        assert isinstance(data["types"], list)
        assert len(data["types"]) > 0
