"""Modèles pour les statistiques."""

from typing import List

from pydantic import BaseModel, Field


class OverviewResponse(BaseModel):
    """Vue d'ensemble des statistiques globales."""

    total_transactions: int = Field(..., description="Nombre total de transactions")
    fraud_rate: float = Field(..., description="Taux de fraude (0-1)")
    avg_amount: float = Field(..., description="Montant moyen des transactions")
    most_common_type: str = Field(
        ..., description="Type de transaction le plus fréquent"
    )


class AmountDistributionBin(BaseModel):
    """Distribution des montants par intervalle."""

    bins: List[str] = Field(
        ..., description="Intervalles de montants (ex: '0-100', '100-500')"
    )
    counts: List[int] = Field(..., description="Nombre de transactions par intervalle")


class StatsByType(BaseModel):
    """Statistiques par type de transaction."""

    type: str = Field(..., description="Type de transaction")
    count: int = Field(..., description="Nombre de transactions")
    avg_amount: float = Field(..., description="Montant moyen")
    total_amount: float = Field(..., description="Montant total")


class DailyStats(BaseModel):
    """Statistiques quotidiennes."""

    day: str = Field(..., description="Date au format YYYY-MM-DD")
    count: int = Field(..., description="Nombre de transactions")
    avg_amount: float = Field(..., description="Montant moyen")
    total_amount: float = Field(..., description="Montant total")
