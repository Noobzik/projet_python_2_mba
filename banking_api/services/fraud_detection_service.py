"""Service de détection de fraude pour l’analyse des fraudes.

Ce module gère la détection, l’analyse et la prédiction de fraude
en utilisant une logique basée sur des règles et des méthodes statistiques.
"""
from typing import List
from banking_api.utils.data_loader import DataLoader
from banking_api.models.schemas import (
    FraudSummary,
    FraudByType,
    FraudPredictionRequest,
    FraudPredictionResponse
)
from banking_api.config import FRAUD_THRESHOLD, HIGH_RISK_AMOUNT


class FraudDetectionService:
    """Classe de service pour les opérations de détection de fraude.

    Attributes
    ----------
    data_loader : DataLoader
        Instance du chargeur de données
    """

    def __init__(self) -> None:
        """Initialiser le service de détection de fraude."""
        self.data_loader = DataLoader()

    def get_fraud_summary(self) -> FraudSummary:
        """Récupérer les statistiques récapitulatives de fraude.

        Returns
        -------
        FraudSummary
            Résumé des statistiques de fraude
        """
        df = self.data_loader.get_data()

        total_frauds = int(df['isFraud'].sum())
        flagged = int(df['isFlaggedFraud'].sum())
        total_transactions = len(df)

        fraud_rate = float(total_frauds / total_transactions) if total_transactions > 0 else 0.0
        detection_rate = float(flagged / total_frauds) if total_frauds > 0 else 0.0

        return FraudSummary(
            total_frauds=total_frauds,
            flagged=flagged,
            fraud_rate=round(fraud_rate, 5),
            detection_rate=round(detection_rate, 4)
        )

    def get_fraud_by_type(self) -> List[FraudByType]:
        """Récupérer les statistiques de fraude par type de transaction.

        Returns
        -------
        List[FraudByType]
            Statistiques de fraude pour chaque type de transaction
        """
        df = self.data_loader.get_data()

        grouped = df.groupby('type').agg({
            'isFraud': ['sum', 'count']
        }).reset_index()

        grouped.columns = ['type', 'fraud_count', 'total_count']

        fraud_by_type = []
        for _, row in grouped.iterrows():
            fraud_count = int(row['fraud_count'])
            total_count = int(row['total_count'])
            fraud_rate = float(fraud_count / total_count) if total_count > 0 else 0.0

            fraud_by_type.append(FraudByType(
                type=str(row['type']),
                fraud_count=fraud_count,
                total_count=total_count,
                fraud_rate=round(fraud_rate, 5)
            ))

        return sorted(fraud_by_type, key=lambda x: x.fraud_rate, reverse=True)

    def predict_fraud(self, request: FraudPredictionRequest) -> FraudPredictionResponse:
        """Prédire la probabilité de fraude pour une transaction.

        Il s’agit d’un système simplifié basé sur des règles,
        utilisant les caractéristiques de la transaction et
        des schémas historiques.

        Parameters
        ----------
        request : FraudPredictionRequest
            Détails de la transaction pour la prédiction

        Returns
        -------
        FraudPredictionResponse
            Résultat de la prédiction avec probabilité et niveau de risque
        """
        risk_score = 0.0

        if request.type in ['TRANSFER', 'CASH_OUT']:
            risk_score += 0.3

        if request.amount > HIGH_RISK_AMOUNT:
            risk_score += 0.4

        balance_diff = abs(request.oldbalanceOrg - request.newbalanceOrig)
        expected_diff = request.amount

        if abs(balance_diff - expected_diff) > 1000:
            risk_score += 0.3

        if request.newbalanceOrig == 0 and request.oldbalanceOrg > 0:
            risk_score += 0.2

        probability = min(risk_score, 1.0)
        is_fraud = probability >= FRAUD_THRESHOLD

        if probability >= 0.7:
            risk_level = "HIGH"
        elif probability >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return FraudPredictionResponse(
            isFraud=is_fraud,
            probability=round(probability, 2),
            risk_level=risk_level
        )