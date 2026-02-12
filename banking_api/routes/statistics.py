"""
Routes pour les statistiques.

Ce module définit les endpoints API pour les agrégations
et analyses statistiques des transactions.
"""

from typing import List

from fastapi import APIRouter

from banking_api.models.schemas import (
    AmountDistribution,
    DailyStats,
    StatsOverview,
    TypeStats,
)
from banking_api.services.stats_service import stats_service

router: APIRouter = APIRouter(prefix="/api/stats", tags=["Statistiques"])


@router.get("/overview", response_model=StatsOverview)
async def get_stats_overview() -> StatsOverview:
    """
    Statistiques globales du dataset.

    Returns
    -------
    StatsOverview
        Vue d'ensemble des statistiques globales incluant:
        - Nombre total de transactions
        - Taux de fraude
        - Montant moyen
        - Type de transaction le plus courant
    """
    return stats_service.get_overview()


@router.get("/amount-distribution", response_model=AmountDistribution)
async def get_amount_distribution() -> AmountDistribution:
    """
    Histogramme du montant des transactions.

    Returns
    -------
    AmountDistribution
        Distribution des montants par classes de valeurs
    """
    return stats_service.get_amount_distribution()


@router.get("/by-type", response_model=List[TypeStats])
async def get_stats_by_type() -> List[TypeStats]:
    """
    Statistiques par type de transaction.

    Returns
    -------
    List[TypeStats]
        Liste des statistiques pour chaque type de transaction incluant:
        - Nombre de transactions
        - Montant moyen
        - Montant total
    """
    return stats_service.get_stats_by_type()


@router.get("/daily", response_model=List[DailyStats])
async def get_daily_stats() -> List[DailyStats]:
    """
    Moyenne et volume des transactions par jour (step).

    Returns
    -------
    List[DailyStats]
        Statistiques quotidiennes incluant:
        - Nombre de transactions par jour
        - Montant moyen
        - Volume total
    """
    return stats_service.get_daily_stats()
