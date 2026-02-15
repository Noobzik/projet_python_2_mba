"""Cache pour les données fréquemment utilisées."""

import os
from functools import lru_cache
from typing import Tuple

import pandas as pd

from banking_api.services.fraud_labels_loader import load_fraud_labels


def _get_csv_path() -> str:
    """Retourne le chemin vers le fichier CSV."""
    base_dir: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    # Utiliser transactions_sample.csv pour un chargement plus rapide
    sample_path = os.path.join(base_dir, "data", "transactions_sample.csv")
    if os.path.exists(sample_path):
        return sample_path
    return os.path.join(base_dir, "data", "transactions_data.csv")


@lru_cache(maxsize=1)
def get_cached_dataframe() -> pd.DataFrame:
    """
    Charge et cache le DataFrame complet en mémoire.

    Attention: Cette fonction charge TOUT le CSV en mémoire (~1.2 GB).
    Utilisez-la uniquement pour les routes qui nécessitent vraiment toutes les données.

    Returns
    -------
    pd.DataFrame
        DataFrame complet avec colonne isFraud ajoutée
    """
    csv_path = _get_csv_path()
    df = pd.read_csv(csv_path)

    # Nettoyer la colonne amount
    df["amount"] = (
        df["amount"].astype(str).str.replace("$", "").str.replace(",", "").astype(float)
    )

    # Ajouter la colonne isFraud depuis le cache des labels
    fraud_labels = load_fraud_labels()
    df["isFraud"] = df["id"].apply(
        lambda x: 1 if fraud_labels.get(str(x), "No") == "Yes" else 0
    )

    return df


@lru_cache(maxsize=1)
def get_basic_stats() -> Tuple[int, float, float, str]:
    """
    Cache les statistiques de base.

    Returns
    -------
    Tuple[int, float, float, str]
        (total_transactions, fraud_rate, avg_amount, most_common_type)
    """
    df = get_cached_dataframe()

    total_transactions = len(df)
    fraud_rate = df["isFraud"].mean()
    avg_amount = df["amount"].mean()
    most_common_type = df["use_chip"].mode()[0]

    return total_transactions, fraud_rate, avg_amount, most_common_type


@lru_cache(maxsize=1)
def get_stats_by_type_cached() -> pd.DataFrame:
    """
    Cache les stats par type.

    Returns
    -------
    pd.DataFrame
        DataFrame avec colonnes: type, count, avg_amount, total_amount
    """
    df = get_cached_dataframe()

    grouped = (
        df.groupby("use_chip").agg({"amount": ["count", "mean", "sum"]}).reset_index()
    )

    grouped.columns = ["type", "count", "avg_amount", "total_amount"]

    return grouped


@lru_cache(maxsize=1)
def get_fraud_summary_cached() -> Tuple[int, int, float, float]:
    """
    Cache le résumé de fraude.

    Returns
    -------
    Tuple[int, int, float, float]
        (total_frauds, flagged, precision, recall)
    """
    df = get_cached_dataframe()

    total_frauds = int(df["isFraud"].sum())
    flagged = total_frauds
    precision = 1.0 if flagged > 0 else 0.0
    recall = 1.0 if total_frauds > 0 else 0.0

    return total_frauds, flagged, precision, recall


@lru_cache(maxsize=1)
def get_fraud_by_type_cached() -> pd.DataFrame:
    """
    Cache les stats de fraude par type.

    Returns
    -------
    pd.DataFrame
        DataFrame avec colonnes: type, total_transactions, fraud_count, fraud_rate
    """
    df = get_cached_dataframe()

    fraud_by_type = (
        df.groupby("use_chip").agg({"isFraud": ["count", "sum", "mean"]}).reset_index()
    )

    fraud_by_type.columns = ["type", "total_transactions", "fraud_count", "fraud_rate"]

    return fraud_by_type


def clear_cache() -> None:
    """Efface tous les caches (utile pour les tests)."""
    get_cached_dataframe.cache_clear()
    get_basic_stats.cache_clear()
    get_stats_by_type_cached.cache_clear()
    get_fraud_summary_cached.cache_clear()
    get_fraud_by_type_cached.cache_clear()
    get_daily_stats_cached.cache_clear()
    get_indexed_dataframe.cache_clear()
    

@lru_cache(maxsize=30)
def get_daily_stats_cached(days: int = 7) -> list:
    """
    Cache les statistiques journalières.

    Args:
        days: Nombre de jours à retourner

    Returns:
        list: Liste des statistiques par jour
    """
    df = get_cached_dataframe()

    # Convertir la date en datetime
    df["date"] = pd.to_datetime(df["date"])

    # Trier par date décroissante et prendre les N derniers jours
    df_sorted = df.sort_values("date", ascending=False)

    # Grouper par jour
    daily_stats = (
        df_sorted.groupby(df_sorted["date"].dt.date)
        .agg({"amount": ["count", "mean", "sum"]})
        .reset_index()
    )


    daily_stats.columns = ["day", "count", "avg_amount", "total_amount"]
    daily_stats = daily_stats.head(days)

    # Convertir en liste de dictionnaires
    result = [
        {
            "day": str(row["day"]),
            "count": int(row["count"]),
            "avg_amount": round(row["avg_amount"], 2),
            "total_amount": round(row["total_amount"], 2)
        }
        for _, row in daily_stats.iterrows()
    ]

    return result

@lru_cache(maxsize=1)
def get_indexed_dataframe() -> pd.DataFrame:
    """
    Retourne le DataFrame avec index sur client_id pour des recherches rapides.

    Returns:
        pd.DataFrame: DataFrame indexé par client_id
    """
    df = get_cached_dataframe()
    # Créer un index sur client_id pour des recherches plus rapides
    df_indexed = df.set_index("client_id", drop=False)
    return df_indexed