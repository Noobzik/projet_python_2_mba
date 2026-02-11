"""Statistics service layer.

This module provides business logic for statistical operations.
"""

from typing import List
import pandas as pd
import numpy as np
from ..models.stats import (
    StatsOverview,
    AmountDistribution,
    TypeStats,
    DailyStats
)
from ..utils.data_loader import DataLoader


class StatsService:
    """Service for statistical operations.

    This service handles calculation of various statistics
    and aggregations on transaction data.
    """

    def __init__(self) -> None:
        """Initialize the statistics service."""
        self.data_loader = DataLoader()

    def get_overview(self) -> StatsOverview:
        """Get overall statistics of the dataset.

        Returns
        -------
        StatsOverview
            Overall statistics including totals, averages, and fraud rate.
        """
        df = self.data_loader.get_data()

        total_transactions = len(df)
        fraud_count = df['isFraud'].sum()
        fraud_rate = fraud_count / total_transactions if total_transactions > 0 else 0
        avg_amount = float(df['amount'].mean())
        total_amount = float(df['amount'].sum())

        # Most common transaction method instead of type
        most_common_type = df['use_chip'].mode()[0] if len(df) > 0 else "Unknown"

        return StatsOverview(
            total_transactions=total_transactions,
            fraud_rate=fraud_rate,
            avg_amount=avg_amount,
            most_common_type=most_common_type,
            total_amount=total_amount
        )

    def get_amount_distribution(self, num_bins: int = 10) -> AmountDistribution:
        """Get distribution of transaction amounts.

        Parameters
        ----------
        num_bins : int
            Number of bins for the histogram.

        Returns
        -------
        AmountDistribution
            Distribution of amounts across bins.
        """
        df = self.data_loader.get_data()

        counts, bin_edges = np.histogram(df['amount'], bins=num_bins)

        bins = [
            f"{int(bin_edges[i])}-{int(bin_edges[i+1])}"
            for i in range(len(bin_edges) - 1)
        ]

        return AmountDistribution(
            bins=bins,
            counts=counts.tolist()
        )

    def get_stats_by_type(self) -> List[TypeStats]:
        """Get statistics grouped by transaction method (use_chip).

        Returns
        -------
        List[TypeStats]
            List of statistics for each transaction method.
        """
        df = self.data_loader.get_data()

        # Use vectorized groupby for better performance
        grouped = df.groupby('use_chip', dropna=True).agg({
            'amount': ['mean', 'sum', 'count'],
            'isFraud': 'sum'
        }).reset_index()

        grouped.columns = pd.Index([
            'type', 'avg_amount', 'total_amount', 'count', 'fraud_count'
        ])

        type_stats = []
        # iterrows is okay here because number of types is very small
        for _, row in grouped.iterrows():
            avg_amount = row['avg_amount'] if not pd.isna(row['avg_amount']) else 0.0
            total_amount = (
                row['total_amount'] if not pd.isna(row['total_amount']) else 0.0
            )

            type_stats.append(TypeStats(
                type=str(row['type']),
                count=int(row['count']),
                avg_amount=float(avg_amount),
                total_amount=float(total_amount),
                fraud_rate=(
                    float(row['fraud_count'] / row['count'])
                    if row['count'] > 0 else 0.0
                )
            ))

        return sorted(type_stats, key=lambda x: x.count, reverse=True)

    def get_daily_stats(self, limit: int = 30) -> List[DailyStats]:
        """Get statistics grouped by date.

        Parameters
        ----------
        limit : int
            Maximum number of daily stats to return (default: 30).
            Use 0 for all days.

        Returns
        -------
        List[DailyStats]
            List of daily statistics.
        """
        df = self.data_loader.get_data()

        # Create a copy to avoid modifying the cached dataframe
        df = df.copy()

        # Ensure we have date parsed. If not, try to parse
        if df['date'].dtype == 'object':
            df['date'] = pd.to_datetime(df['date'])

        # Group by date using pd.Grouper for better performance
        # Resample by Day ('D')
        grouped = df.groupby(pd.Grouper(key='date', freq='D')).agg({
            'amount': ['mean', 'sum', 'count'],
            'isFraud': 'sum'
        }).reset_index()

        grouped.columns = pd.Index([
            'date', 'avg_amount', 'total_amount', 'count', 'fraud_count'
        ])

        # Filter out empty days (count == 0) if any
        grouped = grouped[grouped['count'] > 0]

        grouped = grouped.sort_values('date')

        # Apply limit if specified
        if limit > 0:
            grouped = grouped.tail(limit)

        daily_stats = []
        for _, row in grouped.iterrows():
            avg_amount = (
                row['avg_amount'] if not pd.isna(row['avg_amount']) else 0.0
            )
            total_amount = (
                row['total_amount'] if not pd.isna(row['total_amount']) else 0.0
            )

            # date is now Timestamp, convert to string
            step_str = row['date'].strftime('%Y-%m-%d')

            daily_stats.append(DailyStats(
                step=step_str,
                count=int(row['count']),
                avg_amount=float(avg_amount),
                total_amount=float(total_amount),
                fraud_count=int(row['fraud_count'])
            ))

        return daily_stats
