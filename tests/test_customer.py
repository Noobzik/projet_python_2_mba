import pytest
from fastapi.testclient import TestClient
from app.router.customer import router_customers 
from fastapi import FastAPI
import pandas as pd
from app.services.customers import list_customers, top_customers, stats_by_type, amount_distribution

#Test app.router.customer
# Créer une instance FastAPI pour tester les routes
app = FastAPI()
app.include_router(router_customers)

client = TestClient(app)

def test_list_customers_route():
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Vérifie que chaque élément est une chaîne (un ID client)
    if len(data) > 0:
        assert isinstance(data[0], str)

def test_get_top_customers_default():
    response = client.get("/api/customers/top")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10

def test_get_top_customers_custom_n():
    n = 5
    response = client.get(f"/api/customers/top?n={n}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= n

#test app.services.customer

# Fixture : DataFrame simulé

@pytest.fixture
def sample_df():
    data = {
        "Sender Account ID": ["ACC1", "ACC2", "ACC1", "ACC3", None],
        "Receiver Account ID": ["ACC4", "ACC5", "ACC6", "ACC1", "ACC2"],
        "Transaction Amount": [100, 200, 150, 300, 50],
        "Transaction Type": ["Deposit", "Withdrawal", "Deposit", "Transfer", "Deposit"]
    }
    return pd.DataFrame(data)

# list_customers

def test_list_customers_returns_unique_ids(sample_df):
    result = list_customers(sample_df)
    expected_ids = ["ACC1", "ACC2", "ACC3", "ACC4", "ACC5", "ACC6"]
    # Vérifie que toutes les valeurs sont présentes
    for cid in expected_ids:
        assert cid in result
    # Vérifie qu'il n'y a pas de doublons
    assert len(result) == len(set(result))

# top_customers

def test_top_customers_default_n(sample_df):
    result = top_customers(sample_df)
    # Vérifie que le top par défaut renvoie 10 ou moins
    assert isinstance(result, list)
    assert all("customer_id" in r and "total_amount" in r for r in result)

def test_top_customers_correct_sum(sample_df):
    result = top_customers(sample_df)
    # ACC1 a envoyé 100 + 150 = 250
    acc1 = next(r for r in result if r["customer_id"] == "ACC1")
    assert acc1["total_amount"] == 250

def test_top_customers_limit(sample_df):
    result = top_customers(sample_df, n=2)
    assert len(result) == 2

# stats_by_type

def test_stats_by_type_structure(sample_df):
    result = stats_by_type(sample_df)
    # Chaque entrée doit avoir transaction_type, count, avg_amount
    for r in result:
        assert "transaction_type" in r
        assert "count" in r
        assert "avg_amount" in r

def test_stats_by_type_values(sample_df):
    result = stats_by_type(sample_df)
    deposit = next(r for r in result if r["transaction_type"] == "Deposit")
    # Deposit count = 3, moyenne = (100 + 150 + 50)/3 = 100
    assert deposit["count"] == 3
    assert deposit["avg_amount"] == 100

# amount_distribution

def test_amount_distribution_default_bins(sample_df):
    result = amount_distribution(sample_df)
    assert "labels" in result and "counts" in result
    assert sum(result["counts"]) == len(sample_df)

def test_amount_distribution_custom_bins(sample_df):
    bins = [0, 100, 200, 500]
    result = amount_distribution(sample_df, bins=bins)
    assert result["labels"] == ["0-100", "100-200", "200-500"]
    # Vérifie que le total des transactions est correct
    assert sum(result["counts"]) == len(sample_df)
