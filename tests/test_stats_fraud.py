import pytest
import pandas as pd
from app.services.stats import (
    stats_by_type,
    amount_distribution,
    obtenir_stats_journalieres_completes,
    calculer_taux_fraude_par_type,
    calculer_resume_fraude,
    simuler_prediction_fraude
)

# Dataset de test

df_test = pd.DataFrame([
    {"Transaction Type": "Deposit", "Transaction Amount": 100, "Fraud Flag": False, "Transaction Status": "Success", "Timestamp": "2026-02-01"},
    {"Transaction Type": "Withdrawal", "Transaction Amount": 50, "Fraud Flag": True, "Transaction Status": "Failed", "Timestamp": "2026-02-01"},
    {"Transaction Type": "Deposit", "Transaction Amount": 200, "Fraud Flag": False, "Transaction Status": "Success", "Timestamp": "2026-02-02"},
    {"Transaction Type": "Transfer", "Transaction Amount": 4000, "Fraud Flag": True, "Transaction Status": "Success", "Timestamp": "2026-02-02"},
])

# Tests stats_by_type

def test_stats_by_type():
    result = stats_by_type(df_test)
    types = [r["Transaction Type"] for r in result]
    assert "Deposit" in types
    assert "Withdrawal" in types
    # Vérifie que le count correspond au nombre de transactions
    deposit_stats = next(r for r in result if r["Transaction Type"] == "Deposit")
    assert deposit_stats["count"] == 2

# Tests amount_distribution

def test_amount_distribution_default_bins():
    result = amount_distribution(df_test)
    assert "bins" in result
    assert "counts" in result
    assert sum(result["counts"]) == len(df_test)

def test_amount_distribution_custom_bins():
    bins = [0, 100, 200, 5000]
    result = amount_distribution(df_test, bins=bins)
    assert result["bins"][0] == "0-100"
    assert sum(result["counts"]) == len(df_test)

# Tests obtenir_stats_journalieres_completes

def test_obtenir_stats_journalieres_completes():
    result = obtenir_stats_journalieres_completes(df_test)
    dates = [r["date"].strftime("%Y-%m-%d") for r in result]
    assert "2026-02-01" in dates
    assert "2026-02-02" in dates
    # Vérifie le volume
    volume_0201 = next(r for r in result if r["date"].strftime("%Y-%m-%d") == "2026-02-01")
    assert volume_0201["volume"] == 2

# Tests calculer_taux_fraude_par_type

def test_calculer_taux_fraude_par_type():
    result = calculer_taux_fraude_par_type(df_test)
    deposit = next(r for r in result if r["type"] == "Deposit")
    transfer = next(r for r in result if r["type"] == "Transfer")
    # Deposit n’a qu’une fraude sur 2 → 0.0
    assert deposit["fraud_rate"] == 0.0
    # Transfer a une fraude sur 1 → 1.0
    assert transfer["fraud_rate"] == 1.0

# Tests calculer_resume_fraude

def test_calculer_resume_fraude():
    result = calculer_resume_fraude(df_test)
    # Total fraude = 2
    assert result["total_frauds"] == 2
    # Flagged = 1 (Fraud=True et Status=Failed)
    assert result["flagged"] == 1
    assert result["precision"] == 0.95
    assert result["recall"] == 0.88

# Tests simuler_prediction_fraude

def test_simuler_prediction_fraude_transfer_high_amount():
    result = simuler_prediction_fraude("TRANSFER", 4000, 5000, 1000)
    # Montant élevé + type TRANSFER → score élevé → fraude
    assert result["isFraud"] is True
    assert 0 <= result["probability"] <= 0.99

def test_simuler_prediction_fraude_normal_amount():
    result = simuler_prediction_fraude("DEPOSIT", 100, 1000, 900)
    # Montant normal + type non risky → probablement pas fraude
    assert result["isFraud"] is False
    assert 0 <= result["probability"] <= 0.5
