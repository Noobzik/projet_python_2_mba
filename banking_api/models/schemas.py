"""Schémas supplémentaires pour les réponses statistiques, fraude et système.

Ce module définit les modèles Pydantic pour les réponses API.
"""
from pydantic import BaseModel, Field


class StatsOverview(BaseModel):
    """Réponse des statistiques globales."""

    total_transactions: int
    fraud_rate: float
    avg_amount: float
    most_common_type: str


class AmountDistribution(BaseModel):
    """Réponse de l’histogramme de distribution des montants."""

    bins: list[str]
    counts: list[int]


class TypeStats(BaseModel):
    """Statistiques par type de transaction."""

    type: str
    count: int
    avg_amount: float
    total_amount: float


class DailyStats(BaseModel):
    """Réponse des statistiques journalières."""

    step: int
    count: int
    avg_amount: float
    total_amount: float


class FraudSummary(BaseModel):
    """Résumé de la détection de fraude."""

    total_frauds: int
    flagged: int
    fraud_rate: float
    detection_rate: float
    precision: float = 0.95
    recall: float = 0.88


class FraudByType(BaseModel):
    """Statistiques de fraude par type de transaction."""

    type: str
    fraud_count: int
    total_count: int
    fraud_rate: float


class FraudPredictionRequest(BaseModel):
    """Requête pour la prédiction de fraude."""

    type: str = Field(..., description="Type de transaction")
    amount: float = Field(..., ge=0, description="Montant de la transaction")
    oldbalanceOrg: float = Field(..., ge=0, description="Ancien solde du compte émetteur")
    newbalanceOrig: float = Field(..., ge=0, description="Nouveau solde du compte émetteur")


class FraudPredictionResponse(BaseModel):
    """Réponse pour la prédiction de fraude."""

    isFraud: bool
    probability: float
    risk_level: str


class CustomerProfile(BaseModel):
    """Résumé du profil client."""

    id: str
    transactions_count: int
    avg_amount: float
    total_amount: float
    fraudulent: bool
    fraud_count: int


class CustomerListResponse(BaseModel):
    """Réponse paginée de la liste des clients."""

    page: int
    limit: int
    total: int
    customers: list[str]


class TopCustomer(BaseModel):
    """Meilleur client selon le volume de transactions."""

    customer_id: str
    total_volume: float
    transaction_count: int


class HealthResponse(BaseModel):
    """Réponse du contrôle de santé du système."""

    status: str
    uptime: str
    dataset_loaded: bool
    total_records: int


class MetadataResponse(BaseModel):
    """Réponse des métadonnées système."""

    version: str
    last_update: str
    total_endpoints: int
    dataset_info: dict[str, str | int]
