"""Service de détection et analyse de fraude."""

import os
from typing import Any, Dict, List

from fastapi import HTTPException

from banking_api.services.data_cache import (
    get_fraud_by_type_cached,
    get_fraud_summary_cached,
)


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


def get_fraud_summary() -> Dict[str, Any]:
    """
    Vue d'ensemble de la fraude dans le dataset (avec cache).

    Returns
    -------
    Dict[str, Any]
        Dictionnaire contenant :
        - total_frauds : nombre total de fraudes
        - flagged : nombre de fraudes détectées
        - precision : précision de la détection
        - recall : rappel de la détection
    """
    try:
        # Utiliser le cache pour des performances optimales
        total_frauds, flagged, precision, recall = get_fraud_summary_cached()

        return {
            "total_frauds": int(total_frauds),
            "flagged": int(flagged),
            "precision": round(precision, 2),
            "recall": round(recall, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul: {str(e)}")


def get_fraud_by_type() -> List[Dict[str, Any]]:
    """
    Répartition du taux de fraude par type de transaction (avec cache).

    Returns
    -------
    List[Dict[str, Any]]
        Liste de dictionnaires contenant pour chaque type :
        - type : type de transaction
        - total_transactions : nombre total de transactions
        - fraud_count : nombre de fraudes
        - fraud_rate : taux de fraude (%)
    """
    try:
        # Utiliser le cache
        fraud_by_type = get_fraud_by_type_cached()

        # Convertir en liste de dictionnaires
        results: List[Dict[str, Any]] = []
        for _, row in fraud_by_type.iterrows():
            results.append(
                {
                    "type": row["type"],
                    "total_transactions": int(row["total_transactions"]),
                    "fraud_count": int(row["fraud_count"]),
                    "fraud_rate": round(
                        float(row["fraud_rate"]) * 100, 2
                    ),  # Convertir en pourcentage
                }
            )

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul: {str(e)}")


def predict_fraud(
    transaction_type: str,
    amount: float,
    merchant_city: str = "",
    merchant_state: str = "",
) -> Dict[str, Any]:
    """
    Prédiction simple de fraude basée sur des règles heuristiques.

    Parameters
    ----------
    transaction_type : str
        Type de transaction (use_chip)
    amount : float
        Montant de la transaction
    merchant_city : str
        Ville du marchand
    merchant_state : str
        État du marchand

    Returns
    -------
    Dict[str, Any]
        Dictionnaire contenant :
        - isFraud : prédiction booléenne
        - probability : probabilité estimée de fraude
        - reasons : liste des raisons de la prédiction
    """
    is_fraud: bool = False
    probability: float = 0.0
    reasons: List[str] = []

    # Règle 1 : Montant élevé
    if amount > 10000:
        probability += 0.4
        reasons.append("Montant très élevé")

    # Règle 2 : Montant négatif (remboursement ou erreur)
    if amount < 0:
        probability += 0.5
        reasons.append("Montant négatif détecté")

    # Règle 3 : Transaction Swipe avec montant très élevé
    if transaction_type == "Swipe Transaction" and amount > 5000:
        probability += 0.3
        reasons.append("Swipe transaction avec montant élevé")

    # Règle 4 : Transaction Online avec montant élevé (plus risqué)
    if transaction_type == "Online Transaction" and amount > 3000:
        probability += 0.25
        reasons.append("Transaction en ligne avec montant élevé")

    # Règle 5 : Montant très faible (test de carte volée)
    if 0 < amount < 1:
        probability += 0.1
        reasons.append("Montant très faible (test potentiel)")

    # Limiter la probabilité à 1.0
    probability = min(probability, 1.0)

    # Décision finale
    if probability >= 0.5:
        is_fraud = True

    return {
        "isFraud": is_fraud,
        "probability": round(probability, 2),
        "reasons": reasons if is_fraud else ["Transaction normale"],
    }
