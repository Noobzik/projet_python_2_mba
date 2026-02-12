"""Service de statistiques pour les opérations analytiques.

Ce module gère tous les calculs statistiques et agrégations
pour l'analyse des données de transactions.
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
    """Classe de service pour les opérations statistiques.

    Notes
    -----
    Ce service fournit des analyses agrégées et des statistiques
    descriptives sur l'ensemble du dataset de transactions.
    """

    def __init__(self) -> None:
        """Initialiser le service de statistiques.

        Notes
        -----
        Instancie le DataLoader pour accéder aux données des transactions.
        """
        self.data_loader = DataLoader()

    def get_overview(self) -> StatsOverview:
        """Calculer les statistiques globales du dataset.

        Returns
        -------
        StatsOverview
            Objet contenant :
            - total_transactions : Nombre total de transactions
            - fraud_rate : Taux de fraude (pourcentage)
            - avg_amount : Montant moyen des transactions
            - most_common_type : Type de transaction le plus fréquent

        Examples
        --------
        >>> service = StatsService()
        >>> overview = service.get_overview()
        >>> print(overview.total_transactions)
        6362620
        >>> print(overview.fraud_rate)
        0.00129

        Notes
        -----
        Le taux de fraude est arrondi à 5 décimales pour plus de précision.
        Le montant moyen est arrondi à 2 décimales (format monétaire).
        """
        df = self.data_loader.get_data()

        total_transactions = len(df)
        fraud_count = df['isFraud'].sum()
        fraud_rate = (
            float(fraud_count / total_transactions)
            if total_transactions > 0
            else 0.0
        )
        avg_amount = float(df['amount'].mean())
        most_common_type = (
            str(df['type'].mode()[0])
            if len(df) > 0
            else "N/A"
        )

        return StatsOverview(
            total_transactions=total_transactions,
            fraud_rate=round(fraud_rate, 5),
            avg_amount=round(avg_amount, 2),
            most_common_type=most_common_type
        )

    def get_amount_distribution(self) -> AmountDistribution:
        """Calculer l'histogramme de distribution des montants.

        Returns
        -------
        AmountDistribution
            Objet contenant :
            - bins : Liste des intervalles de montants
            - counts : Nombre de transactions dans chaque intervalle

        Examples
        --------
        >>> service = StatsService()
        >>> distribution = service.get_amount_distribution()
        >>> print(distribution.bins)
        ['0-100', '100-500', '500-1K', '1K-5K', '5K-10K', '10K-50K', '50K+']
        >>> print(distribution.counts[0])
        1234567

        Notes
        -----
        Les intervalles sont définis dans la configuration (AMOUNT_BINS).
        Utilise pandas.cut pour la catégorisation automatique.
        """
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
        """Calculer les statistiques par type de transaction.

        Returns
        -------
        List[TypeStats]
            Liste d'objets TypeStats triée par nombre décroissant, contenant :
            - type : Type de transaction
            - count : Nombre de transactions
            - avg_amount : Montant moyen
            - total_amount : Montant total

        Examples
        --------
        >>> service = StatsService()
        >>> stats = service.get_stats_by_type()
        >>> print(stats[0].type)
        'CASH_OUT'
        >>> print(stats[0].count)
        2237500

        Notes
        -----
        Les résultats sont triés par ordre décroissant de fréquence.
        Utile pour identifier les types de transactions les plus courants.
        """
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
        """Calculer les statistiques journalières des transactions.

        Returns
        -------
        List[DailyStats]
            Liste d'objets DailyStats triée par step (temps), contenant :
            - step : Unité de temps (1 step = 1 heure)
            - count : Nombre de transactions
            - avg_amount : Montant moyen
            - total_amount : Montant total

        Examples
        --------
        >>> service = StatsService()
        >>> daily = service.get_daily_stats()
        >>> print(len(daily))
        30
        >>> print(daily[0].step)
        1

        Notes
        -----
        OPTIMISATION : Pour les datasets > 1M lignes, échantillonne 10%
        des données pour améliorer les performances.
        Limite les résultats à 30 périodes maximum pour les graphiques.
        Le 'step' représente une unité de temps horaire dans le dataset.
        """
        df = self.data_loader.get_data()

        # OPTIMISATION : Échantillonnage pour grands datasets
        if len(df) > 1_000_000:
            df = df.sample(n=min(100_000, len(df) // 10), random_state=42)

        grouped = df.groupby('step').agg({
            'amount': ['count', 'mean', 'sum']
        }).reset_index()

        grouped.columns = ['step', 'count', 'avg_amount', 'total_amount']

        # Limiter à 30 périodes pour la visualisation
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
