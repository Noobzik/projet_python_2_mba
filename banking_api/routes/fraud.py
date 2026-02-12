"""
Routes pour la détection de fraude.

Ce module définit les endpoints API pour l'analyse
et la prédiction de fraude.
"""

from typing import List

from fastapi import APIRouter

from banking_api.models.schemas import (
    FraudByType,
    FraudPredictionRequest,
    FraudPredictionResponse,
    FraudSummary,
)
from banking_api.services.fraud_detection_service import fraud_detection_service

router: APIRouter = APIRouter(prefix="/api/fraud", tags=["Fraude"])


@router.get("/summary", response_model=FraudSummary)
async def get_fraud_summary() -> FraudSummary:
    """
    Vue d'ensemble de la fraude.

    Returns
    -------
    FraudSummary
        Résumé des statistiques de fraude incluant:
        - Nombre total de fraudes
        - Nombre de fraudes signalées
        - Précision de détection
        - Rappel de détection
    """
    return fraud_detection_service.get_fraud_summary()


@router.get("/by-type", response_model=List[FraudByType])
async def get_fraud_by_type() -> List[FraudByType]:
    """
    Répartition du taux de fraude par type de transaction.

    Returns
    -------
    List[FraudByType]
        Liste des statistiques de fraude par type incluant:
        - Nombre de fraudes
        - Nombre total de transactions
        - Taux de fraude
    """
    return fraud_detection_service.get_fraud_by_type()


@router.post("/predict", response_model=FraudPredictionResponse)
async def predict_fraud(
    transaction: FraudPredictionRequest,
) -> FraudPredictionResponse:
    """
    Endpoint de scoring pour prédire si une transaction est frauduleuse.

    Cette implémentation utilise des règles de détection simplifiées.
    En production, un modèle de machine learning devrait être utilisé.

    Parameters
    ----------
    transaction : FraudPredictionRequest
        Données de la transaction à analyser incluant:
        - Type de transaction
        - Montant
        - Solde initial origine
        - Nouveau solde origine

    Returns
    -------
    FraudPredictionResponse
        Prédiction de fraude avec probabilité
    """
    return fraud_detection_service.predict_fraud(transaction)
