"""
Service de détection de fraude.

Ce module fournit les fonctionnalités d'analyse et de détection
de fraude sur les transactions bancaires.
"""

from typing import Any, Dict, List, cast

import pandas as pd

from banking_api.models.schemas import (
    FraudByType,
    FraudPredictionRequest,
    FraudPredictionResponse,
    FraudSummary,
)
from banking_api.services.data_loader import data_loader


class FraudDetectionService:
    """
    Service de détection de fraude.

    Cette classe fournit les opérations d'analyse et de prédiction
    de fraude sur les transactions bancaires.
    """

    def __init__(self) -> None:
        """Initialise le service de détection de fraude."""
        self.data_loader = data_loader

    def get_fraud_summary(self) -> FraudSummary:
        """
        Calcule le résumé de la fraude.

        Returns
        -------
        FraudSummary
            Résumé des statistiques de fraude
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        # Compter les fraudes via errors (non vide = fraude potentielle)
        total_frauds: int = (
            int(df["errors"].notna().sum()) if "errors" in df.columns else 0
        )
        # Les fraudes flaggées sont celles avec des erreurs spécifiques
        flagged: int = (
            int(df["errors"].str.contains("Bad", na=False).sum())
            if "errors" in df.columns
            else 0
        )

        # Calcul de la précision et du rappel (simplifié)
        true_positives: int = flagged
        false_positives: int = 0
        false_negatives: int = total_frauds - flagged

        precision: float = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0.0
        )
        recall: float = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0.0
        )

        return FraudSummary(
            total_frauds=total_frauds,
            flagged=flagged,
            precision=round(precision, 2),
            recall=round(recall, 2),
        )

    def get_fraud_by_type(self) -> List[FraudByType]:
        """
        Calcule la répartition de la fraude par type d'utilisation de carte.

        Returns
        -------
        List[FraudByType]
            Liste des statistiques de fraude par type
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        fraud_stats: List[FraudByType] = []

        for trans_type in df["use_chip"].unique():
            type_df: pd.DataFrame = df[df["use_chip"] == trans_type]
            total_count: int = len(type_df)
            # Compter les fraudes via errors
            fraud_count: int = (
                int(type_df["errors"].notna().sum())
                if "errors" in type_df.columns
                else 0
            )
            fraud_rate: float = fraud_count / total_count if total_count > 0 else 0.0

            fraud_stats.append(
                FraudByType(
                    type=str(trans_type),
                    fraud_count=fraud_count,
                    total_count=total_count,
                    fraud_rate=round(fraud_rate, 4),
                )
            )

        # Tri par taux de fraude décroissant
        fraud_stats.sort(key=lambda x: x.fraud_rate, reverse=True)

        return fraud_stats

    def predict_fraud(
        self, transaction: FraudPredictionRequest
    ) -> FraudPredictionResponse:
        """
        Prédit si une transaction est frauduleuse.

        Cette implémentation utilise des règles simples.
        En production, un modèle ML devrait être utilisé.

        Parameters
        ----------
        transaction : FraudPredictionRequest
            Données de la transaction à analyser

        Returns
        -------
        FraudPredictionResponse
            Prédiction de fraude avec probabilité
        """
        # Règles de détection simplifiées
        fraud_score: float = 0.0

        # Règle 1: Montant élevé
        if transaction.amount > 500:
            fraud_score += 0.3
        if transaction.amount > 1000:
            fraud_score += 0.2

        # Règle 2: Utilisation sans puce (plus risqué)
        if transaction.use_chip == "Swipe Transaction":
            fraud_score += 0.3

        # Règle 3: État à risque (liste simplifiée)
        high_risk_states = ["CA", "TX", "FL", "NY"]
        if transaction.merchant_state in high_risk_states:
            fraud_score += 0.1

        # Règle 4: Catégories MCC à risque (ex: bijoux, électronique)
        high_risk_mcc = [5944, 5732, 5311, 5399]
        if transaction.mcc in high_risk_mcc:
            fraud_score += 0.1

        # Limitation de la probabilité entre 0 et 1
        probability: float = min(fraud_score, 1.0)

        # Seuil de décision
        is_fraud: bool = probability >= 0.5

        return FraudPredictionResponse(
            isFraud=is_fraud, probability=round(probability, 2)
        )

    def get_fraud_patterns(self) -> Dict[str, Any]:
        """
        Analyse les patterns de fraude dans le dataset.

        Returns
        -------
        Dict[str, Any]
            Dictionnaire contenant les patterns détectés
        """
        df: pd.DataFrame = self.data_loader.get_transactions()
        # Fraudes = transactions avec errors non vides
        fraud_df: pd.DataFrame = (
            df[df["errors"].notna()] if "errors" in df.columns else pd.DataFrame()
        )

        if fraud_df.empty:
            return {
                "avg_fraud_amount": 0.0,
                "max_fraud_amount": 0.0,
                "most_common_fraud_type": "NONE",
                "total_fraud_amount": 0.0,
                "fraud_by_chip_type": {},
            }

        patterns: Dict[str, Any] = {
            "avg_fraud_amount": round(float(fraud_df["amount"].mean()), 2),
            "max_fraud_amount": round(float(fraud_df["amount"].max()), 2),
            "most_common_fraud_type": (
                str(fraud_df["use_chip"].mode()[0])
                if not fraud_df["use_chip"].mode().empty
                else "UNKNOWN"
            ),
            "fraud_by_chip_type": fraud_df["use_chip"].value_counts().to_dict(),
            "total_fraud_amount": round(float(fraud_df["amount"].sum()), 2),
        }

        return patterns

    def get_high_risk_transactions(
        self, threshold: float = 0.7, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Identifie les transactions à haut risque.

        Parameters
        ----------
        threshold : float, optional
            Seuil de probabilité de fraude (défaut: 0.7)
        limit : int, optional
            Nombre maximum de transactions à retourner (défaut: 100)

        Returns
        -------
        List[Dict[str, Any]]
            Liste des transactions à haut risque
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        # Calcul d'un score de risque simple pour chaque transaction
        df["risk_score"] = 0.0

        # Montants élevés
        df.loc[df["amount"] > 500, "risk_score"] += 0.3
        df.loc[df["amount"] > 1000, "risk_score"] += 0.2

        # Utilisation sans puce
        df.loc[df["use_chip"] == "Swipe Transaction", "risk_score"] += 0.3

        # Transactions avec erreurs
        if "errors" in df.columns:
            df.loc[df["errors"].notna(), "risk_score"] += 0.4

        # Filtre par seuil
        high_risk_df: pd.DataFrame = df[df["risk_score"] >= threshold].head(limit)

        return cast(List[Dict[str, Any]], high_risk_df.to_dict("records"))


# Instance globale du service
fraud_detection_service: FraudDetectionService = FraudDetectionService()
