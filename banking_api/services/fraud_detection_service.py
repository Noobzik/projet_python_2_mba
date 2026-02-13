"""Service de détection de fraude pour l'analyse des fraudes.

Ce service analyse les transactions pour identifier les fraudes potentielles,
calcule des statistiques de détection et fournit des prédictions.

Contribution: Mame Diarra NDIAYE
"""

from typing import List

from banking_api.config import FRAUD_THRESHOLD, HIGH_RISK_AMOUNT
from banking_api.models.schemas import (FraudByType, FraudPredictionRequest,
                                        FraudPredictionResponse, FraudSummary)
from banking_api.utils.data_loader import DataLoader


class FraudDetectionService:
    """Classe de service pour les opérations de détection de fraude.

    Attributes
    ----------
    data_loader : DataLoader
        Instance du chargeur de données

    Notes
    -----
    Ce service utilise à la fois des analyses statistiques historiques
    et un système de règles pour la prédiction de fraude en temps réel.

    Contribution: Mame Diarra NDIAYE
    """

    def __init__(self) -> None:
        """Initialiser le service de détection de fraude.

        Notes
        -----
        Instancie le DataLoader pour accéder aux données de transactions.
        """
        self.data_loader = DataLoader()

    def get_fraud_summary(self) -> FraudSummary:
        """Récupérer les statistiques récapitulatives de détection de fraude.

        Cette méthode analyse l'ensemble du dataset pour calculer:
        - Le nombre total de fraudes détectées
        - Le nombre de transactions signalées comme suspectes
        - Le taux global de fraude (pourcentage)
        - Les métriques de performance du système de détection

        Returns
        -------
        FraudSummary
            Objet contenant :
            - total_frauds : Nombre total de transactions frauduleuses
            - flagged : Nombre de transactions signalées
            - fraud_rate : Taux de fraude global (0 à 1)
            - detection_rate : Taux de détection des fraudes

        Examples
        --------
        >>> service = FraudDetectionService()
        >>> summary = service.get_fraud_summary()
        >>> print(summary.total_frauds)
        8213
        >>> print(summary.fraud_rate)
        0.00129

        Notes
        -----
        Les valeurs de précision et recall sont des métriques indicatives
        basées sur l'analyse du dataset Kaggle.
        Le taux de fraude est arrondi à 5 décimales pour plus de précision.

        Contribution: Mame Diarra NDIAYE - Documentation des étapes de calcul
        """
        df = self.data_loader.get_data()

        # Calcul du nombre total de transactions frauduleuses détectées
        total_frauds = int(df["isFraud"].sum())

        # Calcul du nombre de transactions signalées (flagged)
        flagged = int(df["isFlaggedFraud"].sum())

        total_transactions = len(df)

        fraud_rate = (
            float(total_frauds / total_transactions) if total_transactions > 0 else 0.0
        )
        detection_rate = float(flagged / total_frauds) if total_frauds > 0 else 0.0

        return FraudSummary(
            total_frauds=total_frauds,
            flagged=flagged,
            fraud_rate=round(fraud_rate, 5),
            detection_rate=round(detection_rate, 4),
        )

    def get_fraud_by_type(self) -> List[FraudByType]:
        """Récupérer les statistiques de fraude par type de transaction.

        Returns
        -------
        List[FraudByType]
            Liste triée par taux de fraude décroissant, contenant :
            - type : Type de transaction
            - fraud_count : Nombre de fraudes
            - total_count : Nombre total de transactions
            - fraud_rate : Taux de fraude pour ce type

        Examples
        --------
        >>> service = FraudDetectionService()
        >>> fraud_stats = service.get_fraud_by_type()
        >>> print(fraud_stats[0].type)
        'TRANSFER'
        >>> print(fraud_stats[0].fraud_rate)
        0.00191

        Notes
        -----
        Les types de transactions sont triés par taux de fraude décroissant
        pour identifier rapidement les types les plus à risque.
        Utile pour adapter les contrôles de sécurité par type.
        """
        df = self.data_loader.get_data()

        # Grouper par type de transaction et compter les occurrences
        grouped = df.groupby("type").agg({"isFraud": ["sum", "count"]}).reset_index()

        grouped.columns = ["type", "fraud_count", "total_count"]

        fraud_by_type = []
        for _, row in grouped.iterrows():
            fraud_count = int(row["fraud_count"])
            total_count = int(row["total_count"])
            fraud_rate = float(fraud_count / total_count) if total_count > 0 else 0.0

            fraud_by_type.append(
                FraudByType(
                    type=str(row["type"]),
                    fraud_count=fraud_count,
                    total_count=total_count,
                    fraud_rate=round(fraud_rate, 5),
                )
            )

        return sorted(fraud_by_type, key=lambda x: x.fraud_rate, reverse=True)

    def predict_fraud(self, request: FraudPredictionRequest) -> FraudPredictionResponse:
        """Prédire la probabilité de fraude pour une transaction.

        Il s'agit d'un système simplifié basé sur des règles,
        utilisant les caractéristiques de la transaction et
        des schémas historiques observés dans le dataset.

        Parameters
        ----------
        request : FraudPredictionRequest
            Objet contenant les détails de la transaction :
            - type : Type de transaction
            - amount : Montant
            - oldbalanceOrg : Solde avant transaction
            - newbalanceOrig : Solde après transaction

        Returns
        -------
        FraudPredictionResponse
            Objet contenant :
            - isFraud : Prédiction binaire (True/False)
            - probability : Score de probabilité (0.0 à 1.0)
            - risk_level : Niveau de risque ('LOW', 'MEDIUM', 'HIGH')

        Examples
        --------
        >>> from banking_api.models.schemas import FraudPredictionRequest
        >>> service = FraudDetectionService()
        >>> request = FraudPredictionRequest(
        ...     type="TRANSFER",
        ...     amount=250000.0,
        ...     oldbalanceOrg=300000.0,
        ...     newbalanceOrig=50000.0
        ... )
        >>> prediction = service.predict_fraud(request)
        >>> print(prediction.risk_level)
        'HIGH'
        >>> print(prediction.probability)
        0.90

        Notes
        -----
        Système basé sur 4 règles principales :
        1. Type de transaction (TRANSFER, CASH_OUT = +0.3)
        2. Montant élevé (> HIGH_RISK_AMOUNT = +0.4)
        3. Incohérence de solde (différence > 1000 = +0.3)
        4. Vidage de compte (nouveau solde = 0 = +0.2)

        Le seuil de décision est défini par FRAUD_THRESHOLD (config).
        Ce système est une version simplifiée à des fins pédagogiques.
        En production, un modèle ML entraîné serait plus adapté.
        """
        risk_score = 0.0

        # Règle 1: Types à risque
        if request.type in ["TRANSFER", "CASH_OUT"]:
            risk_score += 0.3

        # Règle 2: Montants élevés
        if request.amount > HIGH_RISK_AMOUNT:
            risk_score += 0.4

        # Règle 3: Incohérence de solde
        balance_diff = abs(request.oldbalanceOrg - request.newbalanceOrig)
        expected_diff = request.amount

        if abs(balance_diff - expected_diff) > 1000:
            risk_score += 0.3

        # Règle 4: Vidage de compte
        if request.newbalanceOrig == 0 and request.oldbalanceOrg > 0:
            risk_score += 0.2

        # Calcul de la probabilité finale
        probability = min(risk_score, 1.0)
        is_fraud = probability >= FRAUD_THRESHOLD

        # Détermination du niveau de risque
        if probability >= 0.7:
            risk_level = "HIGH"
        elif probability >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return FraudPredictionResponse(
            isFraud=is_fraud, probability=round(probability, 2), risk_level=risk_level
        )
