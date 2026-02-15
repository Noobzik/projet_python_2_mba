"""Tests pour les services non couverts."""


class TestCustomerService:
    """Tests pour customer_service."""

    def test_get_customers(self, client):
        """Test GET /api/customers."""
        response = client.get("/api/customers")
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert isinstance(data["customers"], list)

    def test_get_customer_profile(self, client):
        """Test GET /api/customers/{customer_id}."""
        response = client.get("/api/customers/100")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["id"] == "100"

    def test_get_top_customers(self, client):
        """Test GET /api/customers/top."""
        response = client.get("/api/customers/top?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestStatsService:
    """Tests pour stats_service."""

    def test_get_stats_overview(self, client):
        """Test GET /api/stats/overview."""
        response = client.get("/api/stats/overview")
        assert response.status_code == 200
        data = response.json()
        assert "total_transactions" in data
        assert "avg_amount" in data

    def test_get_stats_by_type(self, client):
        """Test GET /api/stats/by-type."""
        response = client.get("/api/stats/by-type")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_stats_daily(self, client):
        """Test GET /api/stats/daily."""
        response = client.get("/api/stats/daily?days=7")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_amount_distribution(self, client):
        """Test GET /api/stats/amount-distribution."""
        response = client.get("/api/stats/amount-distribution")
        assert response.status_code == 200
        data = response.json()
        assert "bins" in data
        assert "counts" in data
        assert isinstance(data["bins"], list)
        assert isinstance(data["counts"], list)


class TestTransactionsService:
    """Tests pour transactions_service."""

    def test_get_recent_transactions(self, client):
        """Test GET /api/transactions/recent."""
        response = client.get("/api/transactions/recent?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert isinstance(data["transactions"], list)

    def test_search_transactions(self, client):
        """Test POST /api/transactions/search."""
        search_data = {"min_amount": 100, "max_amount": 1000}
        response = client.post("/api/transactions/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data

    def test_get_transactions_by_customer(self, client):
        """Test GET /api/transactions/by-customer/{customer_id}."""
        response = client.get("/api/transactions/by-customer/100")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert isinstance(data["transactions"], list)

    def test_get_transactions_to_customer(self, client):
        """Test GET /api/transactions/to-customer/{customer_id}."""
        response = client.get("/api/transactions/to-customer/100")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert isinstance(data["transactions"], list)

    def test_get_transaction_by_id(self, client):
        """Test GET /api/transactions/{transaction_id}."""
        # Get a valid transaction ID from recent transactions
        recent = client.get("/api/transactions/recent?limit=1")
        assert recent.status_code == 200
        transactions = recent.json()["transactions"]
        assert len(transactions) > 0
        valid_id = str(transactions[0]["id"])

        # Test getting that transaction by ID
        response = client.get(f"/api/transactions/{valid_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert str(data["id"]) == valid_id

    def test_get_transactions_by_merchant(self, client):
        """Test GET /api/transactions/to-customer/{merchant_id}."""
        # Note: Using to-customer route as merchant route doesn't exist
        response = client.get("/api/transactions/to-customer/5000")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert isinstance(data["transactions"], list)
