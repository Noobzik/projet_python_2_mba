from fastapi import APIRouter
from typing import Dict, Any, List
from app.services import stats_service

router = APIRouter()

@router.get("/global", summary="Route 9: KPI Globaux")
def global_statistics() -> Dict[str, Any]:
    """Retourne les KPI globaux (Total, Moyenne, Taux de fraude)."""
    return stats_service.get_global_stats()

@router.get("/by-type", summary="Route 11: Stats par Type")
def statistics_by_type() -> List[Dict[str, Any]]:
    """Répartition des transactions par méthode (Puce, Bande, En ligne)."""
    return stats_service.get_stats_by_type()

@router.get("/amount-distribution", summary="Route 10: Histogramme des montants")
def amount_distribution() -> Dict[str, List[Any]]:
    """
    Répartition des montants par tranches (ex: 0-100$, 100-500$, etc.).
    Indispensable pour l'analyse macro-économique.
    """
    return stats_service.get_amount_distribution()

@router.get("/daily", summary="Route 12: Stats Journalières")
def daily_statistics() -> List[Dict[str, Any]]:
    """
    Volume et montant moyen des transactions par jour.
    Permet de voir les pics d'activité.
    """
    return stats_service.get_daily_stats()

@router.get("/top-sectors", summary="Bonus: Top Secteurs")
def top_sectors(limit: int = 5) -> List[Dict[str, Any]]:
    """Top des secteurs d'activité (Basé sur les codes MCC)."""
    return stats_service.get_top_merchants_categories(limit)