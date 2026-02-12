"""
Data loader utility for Banking Transactions API.

This module handles loading and caching the transaction dataset from CSV.
VERSION SIMPLIFIÉE - Utilise les vraies données sans conversion
"""

import csv
from pathlib import Path
from typing import List, Dict, Any

# Chemin vers le dataset Kaggle
DATA_PATH = Path(__file__).parent.parent / "data" / "transactions_data.csv"

# Cache global
_TRANSACTIONS_CACHE: List[Dict[str, Any]] | None = None

# Limite de transactions à charger (pour éviter les problèmes de mémoire)
MAX_TRANSACTIONS = 100000


def load_transactions() -> List[Dict[str, Any]]:
    """
    Load transaction data from CSV file.

    Returns
    -------
    List[Dict[str, Any]]
        List of transaction dictionaries

    Raises
    ------
    FileNotFoundError
        If CSV file not found
    """
    global _TRANSACTIONS_CACHE

    if _TRANSACTIONS_CACHE is not None:
        return _TRANSACTIONS_CACHE

    print(f"📊 Loading transactions from {DATA_PATH}...")

    try:
        with open(DATA_PATH, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Charger seulement MAX_TRANSACTIONS lignes pour éviter problèmes mémoire
            transactions = []
            for i, row in enumerate(reader):
                if i >= MAX_TRANSACTIONS:
                    print(f"⚠️  Limite atteinte: chargement de {MAX_TRANSACTIONS:,} transactions")
                    break
                transactions.append(row)

            print(f"📦 Processing {len(transactions):,} transactions...")

            # Convert numeric fields and add ID
            for i, tx in enumerate(transactions):
                # Add ID
                tx["id"] = f"tx_{i:07d}"

                # CHECK FORMAT: Card transactions vs Banking transactions
                if "client_id" in tx:
                    # ✅ DATASET CARTE BANCAIRE - Utiliser les VRAIES données
                    tx["step"] = i % 100  # Simuler un step (pas dans le dataset carte)

                    # 🎯 TYPE: Tout en PAYMENT (transaction par carte = paiement)
                    tx["type"] = "PAYMENT"

                    # Clean amount (remove $ and convert)
                    amount_str = str(tx.get("amount", "0"))
                    try:
                        tx["amount"] = float(amount_str.replace("$", "").replace(",", ""))
                    except BaseException:
                        tx["amount"] = 0.0

                    # Create banking fields from card data
                    client_id = str(tx.get('client_id', '0')).strip()
                    merchant_id = str(tx.get('merchant_id', '0')).strip()

                    tx["nameOrig"] = f"C{client_id}"
                    tx["nameDest"] = f"M{merchant_id}"

                    # Soldes: On ne les a pas dans le dataset carte, mettre 0
                    tx["oldbalanceOrg"] = 0.0
                    tx["newbalanceOrig"] = 0.0
                    tx["oldbalanceDest"] = 0.0
                    tx["newbalanceDest"] = 0.0

                    # ✅ FRAUDE: Utiliser la VRAIE colonne "errors"
                    errors_val = str(tx.get("errors", "")).strip()
                    # Si errors est vide ou '0' ou 'No', c'est pas une fraude
                    if errors_val and errors_val not in ["", "0", "No", "no", "NO"]:
                        tx["isFraud"] = 1
                    else:
                        tx["isFraud"] = 0

                    tx["isFlaggedFraud"] = 0

                else:
                    # Already banking format (Paysim dataset)
                    # Convert numeric fields
                    try:
                        tx["step"] = int(tx.get("step", 0))
                        tx["amount"] = float(tx.get("amount", 0))
                        tx["oldbalanceOrg"] = float(tx.get("oldbalanceOrg", 0))
                        tx["newbalanceOrig"] = float(tx.get("newbalanceOrig", 0))
                        tx["oldbalanceDest"] = float(tx.get("oldbalanceDest", 0))
                        tx["newbalanceDest"] = float(tx.get("newbalanceDest", 0))
                        tx["isFraud"] = int(tx.get("isFraud", 0))
                        tx["isFlaggedFraud"] = int(tx.get("isFlaggedFraud", 0))
                    except (ValueError, KeyError) as e:
                        print(f"⚠️  Warning: Error converting transaction {i}: {e}")
                        tx.setdefault("step", 0)
                        tx.setdefault("amount", 0.0)
                        tx.setdefault("oldbalanceOrg", 0.0)
                        tx.setdefault("newbalanceOrig", 0.0)
                        tx.setdefault("oldbalanceDest", 0.0)
                        tx.setdefault("newbalanceDest", 0.0)
                        tx.setdefault("isFraud", 0)
                        tx.setdefault("isFlaggedFraud", 0)

                # Ensure string fields exist
                tx.setdefault("type", "PAYMENT")
                tx.setdefault("nameOrig", "")
                tx.setdefault("nameDest", "")

            _TRANSACTIONS_CACHE = transactions

        print(f"✅ Loaded {len(_TRANSACTIONS_CACHE):,} transactions successfully")

        # Print dataset info
        fraud_count = sum(1 for t in _TRANSACTIONS_CACHE if int(t.get("isFraud", 0)) == 1)
        fraud_rate = (fraud_count / len(_TRANSACTIONS_CACHE) * 100) if _TRANSACTIONS_CACHE else 0
        print(f"📈 Fraud rate: {fraud_rate:.2f}% ({fraud_count:,} fraudulent transactions)")

        # Print type distribution
        type_counts = {}
        for t in _TRANSACTIONS_CACHE:
            tx_type = t.get("type", "UNKNOWN")
            type_counts[tx_type] = type_counts.get(tx_type, 0) + 1

        print("📊 Transaction types:")
        for tx_type, count in type_counts.items():
            pct = (count / len(_TRANSACTIONS_CACHE) * 100) if _TRANSACTIONS_CACHE else 0
            print(f"   - {tx_type}: {count:,} ({pct:.1f}%)")

        return _TRANSACTIONS_CACHE

    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {DATA_PATH}")
        print("📁 Please download the dataset from Kaggle:")
        print("https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets/data")
        print(f"   And place 'transactions_data.csv' in: {DATA_PATH.parent}")

        # Return empty list to avoid crash
        _TRANSACTIONS_CACHE = []
        return _TRANSACTIONS_CACHE

    except Exception as e:
        print(f"❌ ERROR loading transactions: {e}")
        import traceback
        traceback.print_exc()
        _TRANSACTIONS_CACHE = []
        return _TRANSACTIONS_CACHE


def is_loaded() -> bool:
    """
    Check if data is loaded.

    Returns
    -------
    bool
        True if data is loaded
    """
    return _TRANSACTIONS_CACHE is not None and len(_TRANSACTIONS_CACHE) > 0


def reload() -> List[Dict[str, Any]]:
    """
    Force reload of data.

    Returns
    -------
    List[Dict[str, Any]]
        Reloaded transaction list
    """
    global _TRANSACTIONS_CACHE
    _TRANSACTIONS_CACHE = None
    return load_transactions()
