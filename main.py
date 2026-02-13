import pandas as pd
from fastapi import FastAPI
from typing import Dict, Any

from .services.stats_service import get_global_stats
from .services.fraud_detection_service import predict_fraud_logic

app = FastAPI(title="Banking Transactions API", version="1.0.0")


# Chargement du dataset
try:
    df = pd.read_csv("transactions_data.csv")
except Exception:
    df = pd.DataFrame()


@app.get("/api/system/health")
def health_check() -> Dict[str, Any]:
    """
    Vérifie l'état de santé de l'API et le chargement des données.

    Returns
    -------
    Dict[str, Any]
        Dictionnaire contenant le statut 'ok' et l'état du dataset.
    """
    return {
        "status": "ok",
        "dataset_loaded": not df.empty
    }


@app.get("/api/transactions")
def get_transactions(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """
    Récupère la liste des transactions avec un système de pagination.

    Parameters
    ----------
    page : int, optional
        Le numéro de la page à afficher (défaut: 1).
    limit : int, optional
        Le nombre maximum de transactions par page (défaut: 10).

    Returns
    -------
    Dict[str, Any]
        Métadonnées de pagination et liste des transactions extraites.
    """
    start = (page - 1) * limit
    end = start + limit
    items = df.iloc[start:end].to_dict(orient="records") if not df.empty else []
    return {
        "page": page,
        "limit": limit,
        "total": len(df),
        "transactions": items
    }


@app.get("/api/stats/overview")
def route_stats_global() -> Dict[str, Any]:
    """
    Récupère les indicateurs statistiques globaux du dataset.

    Returns
    -------
    Dict[str, Any]
        Statistiques incluant le volume total et le taux de fraude.
    """
    return get_global_stats(df)


@app.post("/api/fraud/predict")
def route_predict_fraud(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prédit si une transaction est frauduleuse via une logique de scoring.

    Parameters
    ----------
    data : Dict[str, Any]
        Données de la transaction à analyser (montant, type, etc.).

    Returns
    -------
    Dict[str, Any]
        Résultat de la prédiction (isFraud) et score de probabilité.
    """
    return predict_fraud_logic(data)
