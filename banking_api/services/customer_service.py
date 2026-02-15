"""Service de gestion des profils clients."""

import os
from typing import Any, Dict, List

import pandas as pd
from fastapi import HTTPException

from banking_api.services.data_cache import get_cached_dataframe


def _get_csv_path() -> str:
    """
    Retourne le chemin vers le fichier CSV de transactions.

    Returns
    -------
    str
        Chemin absolu vers le fichier CSV
    """
    base_dir: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    csv_path: str = os.path.join(base_dir, "data", "transactions_data.csv")
    return csv_path


def get_customers(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """
    Liste paginée des clients extraits de nameOrig.

    Parameters
    ----------
    page : int
        Numéro de la page (défaut: 1)
    limit : int
        Nombre de clients par page (défaut: 10)

    Returns
    -------
    Dict[str, Any]
        Dictionnaire contenant :
        - page : numéro de page
        - limit : limite par page
        - total : nombre total de clients
        - customers : liste des identifiants clients
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        df: pd.DataFrame = pd.read_csv(csv_path)

        # Obtenir les clients uniques (client_id)
        unique_customers: pd.Series = df["client_id"].unique()
        total: int = len(unique_customers)

        # Pagination
        start_idx: int = (page - 1) * limit
        end_idx: int = start_idx + limit

        customers_page: List[int] = unique_customers[start_idx:end_idx].tolist()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "customers": customers_page,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la lecture: {str(e)}"
        )


def get_customer_profile(customer_id: str) -> Dict[str, Any]:
    """
    Profil client synthétique.

    Parameters
    ----------
    customer_id : str
        Identifiant du client

    Returns
    -------
    Dict[str, Any]
        Dictionnaire contenant :
        - id : identifiant du client
        - transactions_count : nombre de transactions
        - avg_amount : montant moyen des transactions
        - total_amount : montant total des transactions
        - fraudulent : indique si le client a été impliqué dans une fraude
        - fraud_count : nombre de fraudes impliquant ce client
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        # Utiliser le DataFrame en cache (déjà nettoyé et avec isFraud)
        df = get_cached_dataframe()

        # Filtrer les transactions du client
        customer_transactions: pd.DataFrame = df[df["client_id"] == int(customer_id)]

        if len(customer_transactions) == 0:
            raise HTTPException(status_code=404, detail="Client non trouvé")

        transactions_count: int = len(customer_transactions)
        avg_amount: float = customer_transactions["amount"].mean()
        total_amount: float = customer_transactions["amount"].sum()
        fraud_count: int = customer_transactions["isFraud"].sum()
        fraudulent: bool = fraud_count > 0

        return {
            "id": customer_id,
            "transactions_count": transactions_count,
            "avg_amount": round(avg_amount, 2),
            "total_amount": round(total_amount, 2),
            "fraudulent": bool(fraudulent),
            "fraud_count": int(fraud_count),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la lecture: {str(e)}"
        )


def get_top_customers(n: int = 10, by: str = "volume") -> List[Dict[str, Any]]:
    """
    Top clients classés par volume total de transactions.

    Parameters
    ----------
    n : int
        Nombre de clients à retourner (défaut: 10)
    by : str
        Critère de classement : "volume" (montant total) ou "count" (nombre de transactions)

    Returns
    -------
    List[Dict[str, Any]]
        Liste des top clients avec leurs statistiques
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        # Utiliser le DataFrame en cache (déjà nettoyé et avec isFraud)
        df = get_cached_dataframe()

        # Grouper par client_id
        customer_stats = (
            df.groupby("client_id")
            .agg({"amount": ["count", "sum", "mean"], "isFraud": "sum"})
            .reset_index()
        )

        # Aplatir les colonnes
        customer_stats.columns = [
            "customer_id",
            "transaction_count",
            "total_amount",
            "avg_amount",
            "fraud_count",
        ]

        # Trier selon le critère
        if by == "count":
            customer_stats = customer_stats.sort_values(
                "transaction_count", ascending=False
            )
        else:  # volume par défaut
            customer_stats = customer_stats.sort_values("total_amount", ascending=False)

        # Prendre les top N
        top_customers = customer_stats.head(n)

        # Convertir en liste de dictionnaires
        results: List[Dict[str, Any]] = []
        for _, row in top_customers.iterrows():
            results.append(
                {
                    "customer_id": int(row["customer_id"]),
                    "transaction_count": int(row["transaction_count"]),
                    "total_amount": round(float(row["total_amount"]), 2),
                    "avg_amount": round(float(row["avg_amount"]), 2),
                    "fraud_count": int(row["fraud_count"]),
                    "fraudulent": int(row["fraud_count"]) > 0,
                }
            )

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul: {str(e)}")
