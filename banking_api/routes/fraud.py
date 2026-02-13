"""Routes de détection de fraude pour l’API.

Ce module définit tous les endpoints liés à la fraude (Routes 13-15).
"""

from typing import List

from fastapi import APIRouter

from banking_api.models.schemas import (FraudByType, FraudPredictionRequest,
                                        FraudPredictionResponse, FraudSummary)
from banking_api.services.fraud_detection_service import FraudDetectionService

router = APIRouter(prefix="/api/fraud", tags=["Fraud Detection"])
service = FraudDetectionService()


@router.get("/summary", response_model=FraudSummary)
async def get_fraud_summary() -> FraudSummary:
    """Récupérer les statistiques récapitulatives de détection de fraude.

    Returns
    -------
    FraudSummary
        Résumé des statistiques de fraude incluant :
        - Nombre total de transactions frauduleuses
        - Nombre de transactions signalées
        - Taux global de fraude
        - Taux de détection
    """
    return service.get_fraud_summary()


@router.get("/by-type", response_model=List[FraudByType])
async def get_fraud_by_type() -> List[FraudByType]:
    """Récupérer les statistiques de fraude par type de transaction.

    Returns
    -------
    List[FraudByType]
        Statistiques de fraude pour chaque type de transaction incluant :
        - Nombre de fraudes
        - Nombre total de transactions
        - Taux de fraude
    """
    return service.get_fraud_by_type()


@router.post("/predict", response_model=FraudPredictionResponse)
async def predict_fraud(request: FraudPredictionRequest) -> FraudPredictionResponse:
    """Prédire la probabilité de fraude pour une transaction donnée.

    Utilise une logique basée sur des règles pour évaluer le risque de fraude selon :
    - Le type de transaction
    - Le montant
    - Les variations de solde

    Parameters
    ----------
    request : FraudPredictionRequest
        Détails de la transaction pour la prédiction

    Returns
    -------
    FraudPredictionResponse
        Résultat de la prédiction incluant :
        - isFraud : prédiction booléenne
        - probability : score de probabilité de fraude (0-1)
        - risk_level : LOW, MEDIUM ou HIGH
    """
    return service.predict_fraud(request)
