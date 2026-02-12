"""Tests unitaires pour le service système.

Ce module teste la classe SystemService.
"""
import pytest
import time
from pathlib import Path
from banking_api.services.system_service import SystemService
from banking_api.utils.data_loader import DataLoader


@pytest.fixture
def service(temp_csv_file: Path) -> SystemService:
    """Créer une instance de SystemService avec des données de test.
    
    Parameters
    ----------
    temp_csv_file : Path
        Chemin vers le fichier CSV temporaire
        
    Returns
    -------
    SystemService
        Instance du service avec les données de test chargées
    """
    loader = DataLoader()
    loader.load_data(temp_csv_file)
    return SystemService()


class TestSystemService:
    """Suite de tests pour SystemService."""
    
    def test_get_health(self, service: SystemService) -> None:
        """Tester le point de contrôle de santé."""
        health = service.get_health()
        
        assert health.status in ['ok', 'degraded']
        assert health.uptime is not None
        assert isinstance(health.dataset_loaded, bool)
        assert health.total_records >= 0
    
    def test_health_uptime_format(self, service: SystemService) -> None:
        """Tester que le temps de fonctionnement est correctement formaté."""
        time.sleep(0.1)
        health = service.get_health()
        
        assert isinstance(health.uptime, str)
        assert len(health.uptime) > 0
    
    def test_health_dataset_loaded(self, service: SystemService) -> None:
        """Tester le statut du dataset chargé dans le contrôle de santé."""
        health = service.get_health()
        
        assert health.dataset_loaded is True
        assert health.total_records == 10
    
    def test_health_status_ok(self, service: SystemService) -> None:
        """Tester que le statut est 'ok' lorsque les données sont chargées."""
        health = service.get_health()
        
        assert health.status == 'ok'
    
    def test_get_metadata(self, service: SystemService) -> None:
        """Tester le point d'accès des métadonnées."""
        metadata = service.get_metadata()
        
        assert metadata.version is not None
        assert metadata.last_update is not None
        assert metadata.total_endpoints == 20
        assert metadata.dataset_info is not None
    
    def test_metadata_version(self, service: SystemService) -> None:
        """Tester que la version est correctement définie."""
        metadata = service.get_metadata()
        
        assert metadata.version == "1.0.0"
    
    def test_metadata_dataset_info(self, service: SystemService) -> None:
        """Tester les informations du dataset dans les métadonnées."""
        metadata = service.get_metadata()
        
        assert 'records' in metadata.dataset_info
        assert 'columns' in metadata.dataset_info
        assert metadata.dataset_info['records'] == 10
    
    def test_uptime_increases(self, service: SystemService) -> None:
        """Tester que le temps de fonctionnement augmente avec le temps."""
        health1 = service.get_health()
        time.sleep(1)
        health2 = service.get_health()
        
        assert health1.uptime != health2.uptime
    
    def test_format_uptime_seconds(self, service: SystemService) -> None:
        """Tester le formatage du temps de fonctionnement en secondes."""
        uptime_str = service._format_uptime(45)
        
        assert '45s' in uptime_str or '45' in uptime_str
    
    def test_format_uptime_minutes(self, service: SystemService) -> None:
        """Tester le formatage du temps de fonctionnement en minutes."""
        uptime_str = service._format_uptime(125)
        
        assert 'm' in uptime_str or 'min' in uptime_str.lower()
    
    def test_format_uptime_with_days(self, service: SystemService) -> None:
        """Tester le formatage de l'uptime avec jours."""
        # Test avec jours, heures, minutes, secondes
        uptime = service._format_uptime(90061)  # 1d 1h 1m 1s
        assert "1d" in uptime
        assert "1h" in uptime
        assert "1m" in uptime
        assert "1s" in uptime
    
    def test_format_uptime_zero(self, service: SystemService) -> None:
        """Tester le formatage avec 0 secondes (edge case)."""
        uptime_zero = service._format_uptime(0)
        assert uptime_zero == "0s"