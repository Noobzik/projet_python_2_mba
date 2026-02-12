"""
Tests de fonctionnalités avec unittest pour les statistiques.

Ce module contient des tests de features pour les statistiques.
"""

import unittest

from fastapi.testclient import TestClient

from banking_api.main import app


class TestStatisticsFeatures(unittest.TestCase):
    """Tests de fonctionnalités pour les statistiques."""

    @classmethod
    def setUpClass(cls) -> None:
        """Configuration initiale de la classe de tests."""
        cls.client = TestClient(app)

    def test_overview_statistics_are_consistent(self) -> None:
        """Test que les statistiques d'ensemble sont cohérentes."""
        response = self.client.get("/api/stats/overview")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Le taux de fraude doit être entre 0 et 1
        self.assertGreaterEqual(data["fraud_rate"], 0.0)
        self.assertLessEqual(data["fraud_rate"], 1.0)

        # Le nombre total doit être positif
        self.assertGreater(data["total_transactions"], 0)

        # Le montant moyen doit être positif
        self.assertGreater(data["avg_amount"], 0)

    def test_stats_by_type_sum_equals_total(self) -> None:
        """Test que la somme des stats par type égale le total."""
        # Récupérer l'overview
        overview_response = self.client.get("/api/stats/overview")
        total_transactions = overview_response.json()["total_transactions"]

        # Récupérer les stats par type
        type_response = self.client.get("/api/stats/by-type")
        type_stats = type_response.json()

        # La somme des counts doit égaler le total
        sum_counts = sum(stat["count"] for stat in type_stats)
        self.assertEqual(sum_counts, total_transactions)

    def test_daily_stats_are_sorted(self) -> None:
        """Test que les statistiques quotidiennes sont triées."""
        response = self.client.get("/api/stats/daily")
        self.assertEqual(response.status_code, 200)
        daily_stats = response.json()

        # Vérifier que les steps sont en ordre croissant
        steps = [stat["step"] for stat in daily_stats]
        self.assertEqual(steps, sorted(steps))

    def test_amount_distribution_bins_are_valid(self) -> None:
        """Test que la distribution des montants est valide."""
        response = self.client.get("/api/stats/amount-distribution")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Le nombre de bins doit égaler le nombre de counts
        self.assertEqual(len(data["bins"]), len(data["counts"]))

        # Tous les counts doivent être positifs ou nuls
        for count in data["counts"]:
            self.assertGreaterEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
