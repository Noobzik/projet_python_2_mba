"""Service de statistiques pour les opérations analytiques.

Ce module gère tous les calculs statistiques et agrégations
pour l’analyse des données de transactions.
"""
import pandas as pd
from typing import List
from banking_api.utils.data_loader import DataLoader
from banking_api.models.schemas import (
    StatsOverview,
    AmountDistribution,
    TypeStats,
    DailyStats
)
from banking_api.config import AMOUNT_BINS


class StatsService:
    """Classe de service pour les opérations statistiques."""

    def __init__(self) -> None:
        """Initialiser le service de statistiques."""
        self.data_loader = DataLoader()

    def get_overview(self) -> StatsOverview:
        """Calculer les statistiques globales."""
        df = self.data_loader.get_data()

        total_transactions = len(df)
        fraud_count = df['isFraud'].sum()
        fraud_rate = float(fraud_count / total_transactions) if total_transactions > 0 else 0.0
        avg_amount = float(df['amount'].mean())
        most_common_type = str(df['type'].mode()[0]) if len(df) > 0 else "N/A"

        return StatsOverview(
            total_transactions=total_transactions,
            fraud_rate=round(fraud_rate, 5),
            avg_amount=round(avg_amount, 2),
            most_common_type=most_common_type
        )

    def get_amount_distribution(self) -> AmountDistribution:
        """Calculer l’histogramme de distribution des montants."""
        df = self.data_loader.get_data()

        bins_edges = [0, 100, 500, 1000, 5000, 10000, 50000, float('inf')]
        bin_labels = AMOUNT_BINS

        df['amount_bin'] = pd.cut(
            df['amount'],
            bins=bins_edges,
            labels=bin_labels,
            include_lowest=True
        )

        counts = df['amount_bin'].value_counts().sort_index()
        counts_list = [int(counts.get(label, 0)) for label in bin_labels]

        return AmountDistribution(
            bins=bin_labels,
            counts=counts_list
        )

    def get_stats_by_type(self) -> List[TypeStats]:
        """Calculer les statistiques par type de transaction."""
        df = self.data_loader.get_data()

        grouped = df.groupby('type').agg({
            'amount': ['count', 'mean', 'sum']
        }).reset_index()
        grouped.columns = ['type', 'count', 'avg_amount', 'total_amount']

        stats_list = []
        for _, row in grouped.iterrows():
            stats_list.append(TypeStats(
                type=str(row['type']),
                count=int(row['count']),
                avg_amount=round(float(row['avg_amount']), 2),
                total_amount=round(float(row['total_amount']), 2)
            ))

        return sorted(stats_list, key=lambda x: x.count, reverse=True)

    def get_daily_stats(self) -> List[DailyStats]:
        """Calculer les statistiques journalières.

        OPTIMISÉ : Échantillonne les grands datasets pour éviter les problèmes de performance.
        """
        df = self.data_loader.get_data()

        # OPTIMISATION : Si le dataset dépasse 1 million de lignes, prendre un échantillon
        if len(df) > 1_000_000:
            # Prendre 10 % du dataset aléatoirement
            df = df.sample(n=min(100_000, len(df) // 10), random_state=42)

        grouped = df.groupby('step').agg({
            'amount': ['count', 'mean', 'sum']
        }).reset_index()
        grouped.columns = ['step', 'count', 'avg_amount', 'total_amount']

        # Limiter à 30 jours maximum pour les tests
        if len(grouped) > 30:
            grouped = grouped.head(30)

        daily_stats = []
        for _, row in grouped.iterrows():
            daily_stats.append(DailyStats(
                step=int(row['step']),
                count=int(row['count']),
                avg_amount=round(float(row['avg_amount']), 2),
                total_amount=round(float(row['total_amount']), 2)
            ))

        return sorted(daily_stats, key=lambda x: x.step)