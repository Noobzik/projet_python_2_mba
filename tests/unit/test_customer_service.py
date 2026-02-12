"""Tests unitaires pour le service client.

Ce module teste la classe CustomerService.
"""
import pytest
from pathlib import Path
from banking_api.services.customer_service import CustomerService
from banking_api.utils.data_loader import DataLoader


@pytest.fixture
def service(temp_csv_file: Path) -> CustomerService:
    """Créer une instance de CustomerService avec des données de test."""
    loader = DataLoader()
    loader.load_data(temp_csv_file)
    return CustomerService()


class TestCustomerService:
    """Suite de tests pour CustomerService."""
    
    def test_get_all_customers_pagination(self, service: CustomerService) -> None:
        """Tester la liste paginée des clients."""
        result = service.get_all_customers(page=1, limit=5)
        
        assert result.page == 1
        assert result.limit == 5
        assert result.total > 0
        assert len(result.customers) <= 5
    
    def test_get_all_customers_unique(self, service: CustomerService) -> None:
        """Tester que la liste des clients contient des identifiants uniques."""
        result = service.get_all_customers(page=1, limit=100)
        
        assert len(result.customers) == len(set(result.customers))
    
    def test_get_customer_profile_exists(self, service: CustomerService) -> None:
        """Tester la récupération du profil d’un client existant."""
        profile = service.get_customer_profile('C001')
        
        assert profile is not None
        assert profile.id == 'C001'
        assert profile.transactions_count > 0
        assert profile.avg_amount > 0
    
    def test_get_customer_profile_not_found(self, service: CustomerService) -> None:
        """Tester la récupération du profil d’un client inexistant."""
        profile = service.get_customer_profile('C9999')
        
        assert profile is None
    
    def test_customer_profile_fraud_detection(self, service: CustomerService) -> None:
        """Tester la détection de fraude dans le profil client."""
        profile = service.get_customer_profile('C001')
        
        assert profile is not None
        assert isinstance(profile.fraudulent, bool)
        assert profile.fraud_count >= 0
    
    def test_customer_profile_transaction_count(self, service: CustomerService) -> None:
        """Tester le nombre de transactions dans le profil client."""
        profile = service.get_customer_profile('C001')
        
        assert profile is not None
        assert profile.transactions_count == 2
    
    def test_get_top_customers(self, service: CustomerService) -> None:
        """Tester la récupération des meilleurs clients par volume."""
        top = service.get_top_customers(n=3)
        
        assert len(top) <= 3
        assert all(c.total_volume > 0 for c in top)
        assert all(c.transaction_count > 0 for c in top)
    
    def test_top_customers_sorted(self, service: CustomerService) -> None:
        """Tester que les meilleurs clients sont triés par volume décroissant."""
        top = service.get_top_customers(n=5)
        
        volumes = [c.total_volume for c in top]
        assert volumes == sorted(volumes, reverse=True)
    
    def test_top_customers_limit(self, service: CustomerService) -> None:
        """Tester que la limite du nombre de meilleurs clients est respectée."""
        top = service.get_top_customers(n=2)
        
        assert len(top) <= 2
    
    def test_customer_profile_amounts(self, service: CustomerService) -> None:
        """Tester les calculs de montants dans le profil client."""
        profile = service.get_customer_profile('C002')
        
        assert profile is not None
        assert profile.avg_amount > 0
        assert profile.total_amount >= profile.avg_amount