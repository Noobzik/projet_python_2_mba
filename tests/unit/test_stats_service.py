"""Tests unitaires pour le service de statistiques.

Ce module teste la classe StatsService.
"""
import pytest
from pathlib import Path
from banking_api.services.stats_service import StatsService
from banking_api.utils.data_loader import DataLoader


@pytest.fixture
def service(temp_csv_file: Path) -> StatsService:
    """Créer une instance de StatsService avec des données de test."""
    loader = DataLoader()
    loader.load_data(temp_csv_file)
    return StatsService()


class TestStatsService:
    """Suite de tests pour StatsService."""
    
    def test_get_overview(self, service: StatsService) -> None:
        """Tester la récupération des statistiques globales."""
        overview = service.get_overview()
        
        assert overview.total_transactions == 10
        assert 0 <= overview.fraud_rate <= 1
        assert overview.avg_amount > 0
        assert overview.most_common_type in ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT', 'CASH_IN']
    
    def test_overview_fraud_rate_calculation(self, service: StatsService) -> None:
        """Tester le calcul du taux de fraude dans les statistiques globales."""
        overview = service.get_overview()
        
        expected_fraud_rate = 3 / 10
        assert abs(overview.fraud_rate - expected_fraud_rate) < 0.01
    
    def test_get_amount_distribution(self, service: StatsService) -> None:
        """Tester l’histogramme de distribution des montants."""
        distribution = service.get_amount_distribution()
        
        assert len(distribution.bins) == len(distribution.counts)
        assert sum(distribution.counts) == 10
        assert all(count >= 0 for count in distribution.counts)
    
    def test_amount_distribution_bins(self, service: StatsService) -> None:
        """Tester que les classes de distribution sont correctes."""
        distribution = service.get_amount_distribution()
        
        expected_bins = ['0-100', '100-500', '500-1000', '1000-5000', 
                         '5000-10000', '10000-50000', '50000+']
        assert distribution.bins == expected_bins
    
    def test_get_stats_by_type(self, service: StatsService) -> None:
        """Tester les statistiques par type de transaction."""
        stats = service.get_stats_by_type()
        
        assert len(stats) > 0
        assert all(s.count > 0 for s in stats)
        assert all(s.avg_amount > 0 for s in stats)
        assert all(s.total_amount > 0 for s in stats)
    
    def test_stats_by_type_payment(self, service: StatsService) -> None:
        """Tester les statistiques pour le type PAYMENT."""
        stats = service.get_stats_by_type()
        payment_stats = next((s for s in stats if s.type == 'PAYMENT'), None)
        
        assert payment_stats is not None
        assert payment_stats.count == 4
    
    def test_get_daily_stats(self, service: StatsService) -> None:
        """Tester les statistiques journalières."""
        daily = service.get_daily_stats()
        
        assert len(daily) == 10
        assert all(d.count > 0 for d in daily)
        assert all(d.avg_amount > 0 for d in daily)
    
    def test_daily_stats_sorted(self, service: StatsService) -> None:
        """Tester que les statistiques journalières sont triées par étape (step)."""
        daily = service.get_daily_stats()
        
        steps = [d.step for d in daily]
        assert steps == sorted(steps)
    
    def test_daily_stats_totals(self, service: StatsService) -> None:
        """Tester que les statistiques journalières s’additionnent correctement."""
        daily = service.get_daily_stats()
        
        total_count = sum(d.count for d in daily)
        assert total_count == 10