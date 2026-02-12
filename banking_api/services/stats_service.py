"""
Service de calcul des statistiques.

Ce module fournit les fonctionnalités d'agrégation et de calcul
des statistiques sur les transactions bancaires.
"""

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from banking_api.models.schemas import (
    AmountDistribution,
    DailyStats,
    StatsOverview,
    TypeStats,
)
from banking_api.services.data_loader import data_loader


class StatsService:
    """
    Service de calcul des statistiques.

    Cette classe fournit toutes les opérations de calcul statistique
    sur les transactions bancaires.
    """

    def __init__(self) -> None:
        """Initialise le service des statistiques."""
        self.data_loader = data_loader

    def get_overview(self) -> StatsOverview:
        """
        Calcule les statistiques globales du dataset.

        Returns
        -------
        StatsOverview
            Vue d'ensemble des statistiques globales
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        total_transactions: int = len(df)
        # Compter les fraudes via la colonne errors (non vide = fraude potentielle)
        fraud_count: int = (
            int(df["errors"].notna().sum()) if "errors" in df.columns else 0
        )
        fraud_rate: float = (
            fraud_count / total_transactions if total_transactions > 0 else 0.0
        )
        avg_amount: float = float(df["amount"].mean())
        # Utiliser use_chip comme type le plus commun
        most_common_type: str = str(
            df["use_chip"].mode()[0] if not df["use_chip"].mode().empty else "UNKNOWN"
        )

        return StatsOverview(
            total_transactions=total_transactions,
            fraud_rate=round(fraud_rate, 5),
            avg_amount=round(avg_amount, 2),
            most_common_type=most_common_type,
        )

    def get_amount_distribution(self, bins: int = 10) -> AmountDistribution:
        """
        Calcule la distribution des montants par classe.

        Parameters
        ----------
        bins : int, optional
            Nombre de classes (défaut: 10)

        Returns
        -------
        AmountDistribution
            Distribution des montants
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        # Création des bins
        counts_array: np.ndarray
        bin_edges: np.ndarray
        counts_array, bin_edges = np.histogram(df["amount"], bins=bins)

        # Formatage des labels de bins
        bin_labels: List[str] = []
        for i in range(len(bin_edges) - 1):
            label: str = f"{int(bin_edges[i])}-{int(bin_edges[i + 1])}"
            bin_labels.append(label)

        return AmountDistribution(bins=bin_labels, counts=counts_array.tolist())

    def get_stats_by_type(self) -> List[TypeStats]:
        """
        Calcule les statistiques par type d'utilisation de carte.

        Returns
        -------
        List[TypeStats]
            Liste des statistiques par type
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        stats_list: List[TypeStats] = []
        for trans_type in df["use_chip"].unique():
            type_df: pd.DataFrame = df[df["use_chip"] == trans_type]
            count: int = len(type_df)
            avg_amount: float = float(type_df["amount"].mean())
            total_amount: float = float(type_df["amount"].sum())

            stats_list.append(
                TypeStats(
                    type=str(trans_type),
                    count=count,
                    avg_amount=round(avg_amount, 2),
                    total_amount=round(total_amount, 2),
                )
            )

        return stats_list

    def get_daily_stats(self) -> List[DailyStats]:
        """
        Calcule les statistiques quotidiennes (par date).

        Returns
        -------
        List[DailyStats]
            Liste des statistiques quotidiennes
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        # Convertir date en datetime et extraire la date (sans heure)
        df["date_only"] = pd.to_datetime(df["date"]).dt.date

        # Groupement par date
        grouped: pd.core.groupby.DataFrameGroupBy = df.groupby("date_only")

        daily_stats_list: List[DailyStats] = []
        for idx, (date_val, group_df) in enumerate(grouped):
            count: int = len(group_df)
            avg_amount: float = float(group_df["amount"].mean())
            total_amount: float = float(group_df["amount"].sum())

            daily_stats_list.append(
                DailyStats(
                    step=idx,  # Utiliser l'index comme step
                    count=count,
                    avg_amount=round(avg_amount, 2),
                    total_amount=round(total_amount, 2),
                )
            )

        # Tri par step
        daily_stats_list.sort(key=lambda x: x.step)

        return daily_stats_list

    def get_custom_aggregation(
        self, group_by: str, metrics: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Effectue une agrégation personnalisée.

        Parameters
        ----------
        group_by : str
            Colonne pour le groupement
        metrics : List[str]
            Liste des métriques à calculer

        Returns
        -------
        List[Dict[str, Any]]
            Résultats de l'agrégation
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        if group_by not in df.columns:
            return []

        grouped: pd.core.groupby.DataFrameGroupBy = df.groupby(group_by)
        results: List[Dict[str, Any]] = []

        for name, group in grouped:
            result: Dict[str, Any] = {group_by: name}

            for metric in metrics:
                if metric == "count":
                    result["count"] = len(group)
                elif metric == "avg_amount":
                    result["avg_amount"] = round(float(group["amount"].mean()), 2)
                elif metric == "total_amount":
                    result["total_amount"] = round(float(group["amount"].sum()), 2)
                elif metric == "fraud_rate":
                    # Calculer le taux de fraude basé sur errors (non vide = fraude)
                    if "errors" in group.columns:
                        fraud_rate: float = group["errors"].notna().mean()
                        result["fraud_rate"] = round(float(fraud_rate), 4)
                    else:
                        result["fraud_rate"] = 0.0

            results.append(result)

        return results


# Instance globale du service
stats_service: StatsService = StatsService()
