"""
Tests unitaires pour le service de statistiques.
"""

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from banking_api.models.schemas import (
    AmountDistribution,
    DailyStats,
    StatsOverview,
    TypeStats,
)
from banking_api.services.stats_service import StatsService


class TestStatsService(unittest.TestCase):
    """Tests pour le service de statistiques."""

    def setUp(self) -> None:
        """Configuration initiale des tests."""
        self.mock_data_loader = MagicMock()

        # Créer un DataFrame de test
        data = {
            "amount": [10.0, 20.0, 100.0, 50.0, 200.0],
            "use_chip": [
                "Chip Transaction",
                "Online Transaction",
                "Chip Transaction",
                "Swipe Transaction",
                "Online Transaction",
            ],
            "errors": [None, "Error", None, None, "Error"],
            "date": [
                "2023-01-01 10:00:00",
                "2023-01-01 11:00:00",
                "2023-01-02 10:00:00",
                "2023-01-02 12:00:00",
                "2023-01-03 10:00:00",
            ],
            "merchant_state": ["CA", "NY", "CA", "TX", "NY"],
        }
        self.test_df = pd.DataFrame(data)

        # Patcher le data_loader dans le service
        self.patcher = patch(
            "banking_api.services.stats_service.data_loader", self.mock_data_loader
        )
        self.patcher.start()

        self.stats_service = StatsService()
        self.mock_data_loader.get_transactions.return_value = self.test_df

    def tearDown(self) -> None:
        """Nettoyage après les tests."""
        self.patcher.stop()

    def test_get_overview(self) -> None:
        """Test de la vue d'ensemble."""
        overview = self.stats_service.get_overview()

        self.assertIsInstance(overview, StatsOverview)
        self.assertEqual(overview.total_transactions, 5)
        self.assertEqual(overview.fraud_rate, 0.4)  # 2 erreurs sur 5
        self.assertEqual(overview.avg_amount, 76.0)  # (10+20+100+50+200)/5 = 76
        self.assertIn(
            overview.most_common_type, ["Chip Transaction", "Online Transaction"]
        )

    def test_get_amount_distribution(self) -> None:
        """Test de la distribution des montants."""
        dist = self.stats_service.get_amount_distribution(bins=2)

        self.assertIsInstance(dist, AmountDistribution)
        self.assertEqual(len(dist.bins), 2)
        self.assertEqual(len(dist.counts), 2)
        self.assertEqual(sum(dist.counts), 5)

    def test_get_stats_by_type(self) -> None:
        """Test des statistiques par type."""
        stats = self.stats_service.get_stats_by_type()

        self.assertIsInstance(stats, list)
        self.assertTrue(len(stats) > 0)
        self.assertIsInstance(stats[0], TypeStats)

        # Vérifier pour Chip Transaction
        chip_stats = next((s for s in stats if s.type == "Chip Transaction"), None)
        self.assertIsNotNone(chip_stats)
        if chip_stats:
            self.assertEqual(chip_stats.count, 2)
            self.assertEqual(chip_stats.total_amount, 110.0)

    def test_get_daily_stats(self) -> None:
        """Test des statistiques quotidiennes."""
        daily_stats = self.stats_service.get_daily_stats()

        self.assertIsInstance(daily_stats, list)
        self.assertEqual(len(daily_stats), 3)  # 3 jours différents
        self.assertIsInstance(daily_stats[0], DailyStats)

        # Vérifier le premier jour (2023-01-01)
        day1 = daily_stats[0]
        self.assertEqual(day1.count, 2)
        self.assertEqual(day1.total_amount, 30.0)

    def test_get_custom_aggregation(self) -> None:
        """Test de l'agrégation personnalisée."""
        # Test group by merchant_state
        metrics = ["count", "avg_amount", "total_amount", "fraud_rate"]
        results = self.stats_service.get_custom_aggregation("merchant_state", metrics)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)  # CA, NY, TX

        # Vérifier NY (2 transactions, 2 erreurs -> 100% fraud)
        ny_stats = next((r for r in results if r["merchant_state"] == "NY"), None)
        self.assertIsNotNone(ny_stats)
        if ny_stats:
            self.assertEqual(ny_stats["count"], 2)
            self.assertEqual(ny_stats["fraud_rate"], 1.0)
            self.assertEqual(ny_stats["total_amount"], 220.0)

    def test_get_custom_aggregation_invalid_column(self) -> None:
        """Test de l'agrégation avec une colonne invalide."""
        results = self.stats_service.get_custom_aggregation("invalid_column", ["count"])
        self.assertEqual(results, [])

    def test_get_overview_empty_df(self) -> None:
        """Test avec un DataFrame vide."""
        self.mock_data_loader.get_transactions.return_value = pd.DataFrame(
            columns=["amount", "use_chip", "errors"]
        )

        overview = self.stats_service.get_overview()
        self.assertEqual(overview.total_transactions, 0)
        self.assertEqual(overview.fraud_rate, 0.0)
        self.assertTrue(np.isnan(overview.avg_amount))
