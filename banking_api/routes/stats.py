"""Routes de statistiques pour l’API.

Ce module définit tous les endpoints liés aux statistiques (Routes 9-12).
"""

from typing import List

from fastapi import APIRouter

from banking_api.models.schemas import (AmountDistribution, DailyStats,
                                        StatsOverview, TypeStats)
from banking_api.services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["Statistics"])
service = StatsService()


@router.get("/overview", response_model=StatsOverview)
async def get_stats_overview() -> StatsOverview:
    """Récupérer les statistiques globales du dataset.

    Returns
    -------
    StatsOverview
        Statistiques globales incluant :
        - Nombre total de transactions
        - Taux de fraude
        - Montant moyen des transactions
        - Type de transaction le plus fréquent
    """
    return service.get_overview()


@router.get("/amount-distribution", response_model=AmountDistribution)
async def get_amount_distribution() -> AmountDistribution:
    """Récupérer l’histogramme de distribution des montants.

    Returns
    -------
    AmountDistribution
        Distribution des montants de transactions selon des classes prédéfinies
    """
    return service.get_amount_distribution()


@router.get("/by-type", response_model=List[TypeStats])
async def get_stats_by_type() -> List[TypeStats]:
    """Récupérer les statistiques agrégées par type de transaction.

    Returns
    -------
    List[TypeStats]
        Statistiques pour chaque type de transaction incluant :
        - Nombre de transactions
        - Montant moyen
        - Montant total
    """
    return service.get_stats_by_type()


@router.get("/daily", response_model=List[DailyStats])
async def get_daily_stats() -> List[DailyStats]:
    """Récupérer les statistiques journalières (par étape).

    Returns
    -------
    List[DailyStats]
        Statistiques pour chaque jour incluant :
        - Nombre de transactions
        - Montant moyen
        - Volume total
    """
    return service.get_daily_stats()
