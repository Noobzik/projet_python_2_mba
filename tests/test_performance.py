import time
import pytest
from fastapi.testclient import TestClient
from app.main import app  

client = TestClient(app)


# Helper pour mesurer le temps d'exécution

def measure_latency(endpoint: str, payload: dict) -> float:
    start_time = time.perf_counter()
    response = client.post(endpoint, json=payload)
    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    assert response.status_code == 200
    return duration_ms


# Test performance pour /api/transactions/search

@pytest.mark.parametrize("limit", [10, 50, 100])
def test_transactions_search_latency(limit):
    payload = {
        "page": 1,
        "limit": limit,
        "tx_type": None,
        "isFraud": None,
        "min_amount": None,
        "max_amount": None
    }
    duration = measure_latency("/api/transactions/search", payload)
    print(f"Transactions {limit} → Latence : {duration:.2f} ms")
    assert duration < 500, f"Latence trop élevée pour {limit} transactions : {duration:.2f} ms"

# Test performance pour /api/transactions/recent

@pytest.mark.parametrize("n", [10, 50, 100])
def test_recent_transactions_latency(n):
    start_time = time.perf_counter()
    response = client.get(f"/api/transactions/recent?n={n}")
    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    assert response.status_code == 200
    print(f"Recent {n} transactions → Latence : {duration_ms:.2f} ms")
    assert duration_ms < 500, f"Latence trop élevée pour {n} transactions : {duration_ms:.2f} ms"


# Option : test boucle pour moyenne de 100 requêtes (optionnel)

@pytest.mark.parametrize("limit", [100])
def test_transactions_search_avg_latency(limit):
    payload = {"page": 1, "limit": limit}
    durations = []
    for _ in range(10):
        durations.append(measure_latency("/api/transactions/search", payload))
    avg_latency = sum(durations)/len(durations)
    print(f"Latence moyenne sur 10 appels ({limit} transactions) : {avg_latency:.2f} ms")
    assert avg_latency < 500, f"Latence moyenne trop élevée : {avg_latency:.2f} ms"
