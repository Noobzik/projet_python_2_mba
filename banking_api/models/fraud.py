"""Modèles pour la détection de fraude."""

from typing import List

from pydantic import BaseModel, Field


class FraudSummary(BaseModel):
    """Résumé de la fraude dans le dataset."""

    total_frauds: int = Field(..., description="Nombre total de fraudes")
    flagged: int = Field(..., description="Nombre de fraudes détectées")
    precision: float = Field(..., description="Précision de la détection (0-1)")
    recall: float = Field(..., description="Rappel de la détection (0-1)")


class FraudByType(BaseModel):
    """Statistiques de fraude par type de transaction."""

    type: str = Field(..., description="Type de transaction")
    total_transactions: int = Field(..., description="Nombre total de transactions")
    fraud_count: int = Field(..., description="Nombre de fraudes")
    fraud_rate: float = Field(..., description="Taux de fraude en pourcentage")


class FraudPrediction(BaseModel):
    """Prédiction de fraude pour une transaction."""

    isFraud: bool = Field(..., description="Prédiction de fraude (True/False)")
    probability: float = Field(..., description="Probabilité de fraude (0-1)")
    reasons: List[str] = Field(..., description="Raisons de la prédiction")
