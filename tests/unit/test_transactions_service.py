"""Tests unitaires pour le service des transactions.

Ce module teste la classe TransactionsService.
"""
import pytest
from pathlib import Path
from banking_api.services.transactions_service import TransactionsService
from banking_api.models.transaction import TransactionSearchRequest
from banking_api.utils.data_loader import DataLoader


@pytest.fixture
def service(temp_csv_file: Path) -> TransactionsService:
    """Créer une instance de TransactionsService avec des données de test."""
    loader = DataLoader()
    loader.load_data(temp_csv_file)
    return TransactionsService()


class TestTransactionsService:
    """Suite de tests pour TransactionsService."""
    
    def test_get_all_transactions_pagination(self, service: TransactionsService) -> None:
        """Tester la pagination des transactions."""
        result = service.get_all_transactions(page=1, limit=5)
        
        assert result.page == 1
        assert result.limit == 5
        assert result.total == 10
        assert len(result.transactions) == 5
    
    def test_get_all_transactions_second_page(self, service: TransactionsService) -> None:
        """Tester la deuxième page des résultats paginés."""
        result = service.get_all_transactions(page=2, limit=5)
        
        assert result.page == 2
        assert len(result.transactions) == 5
    
    def test_filter_by_type(self, service: TransactionsService) -> None:
        """Tester le filtrage par type de transaction."""
        result = service.get_all_transactions(type_filter='PAYMENT')
        
        assert all(t.type == 'PAYMENT' for t in result.transactions)
        assert result.total == 4
    
    def test_filter_by_fraud(self, service: TransactionsService) -> None:
        """Tester le filtrage par statut de fraude."""
        result = service.get_all_transactions(is_fraud=1)
        
        assert all(t.isFraud == 1 for t in result.transactions)
        assert result.total == 3
    
    def test_filter_by_amount_range(self, service: TransactionsService) -> None:
        """Tester le filtrage par intervalle de montant."""
        result = service.get_all_transactions(min_amount=1000.0, max_amount=50000.0)
        
        assert all(1000.0 <= t.amount <= 50000.0 for t in result.transactions)
    
    def test_get_transaction_by_id_exists(self, service: TransactionsService) -> None:
        """Tester la récupération d’une transaction existante."""
        transaction = service.get_transaction_by_id('tx_0')
        
        assert transaction is not None
        assert transaction.id == 'tx_0'
        assert transaction.type == 'PAYMENT'
    
    def test_get_transaction_by_id_not_found(self, service: TransactionsService) -> None:
        """Tester la récupération d’une transaction inexistante."""
        transaction = service.get_transaction_by_id('tx_9999')
        
        assert transaction is None
    
    def test_get_transaction_by_id_invalid_format(self, service: TransactionsService) -> None:
        """Tester un format d’identifiant de transaction invalide."""
        transaction = service.get_transaction_by_id('invalid_id')
        
        assert transaction is None
    
    def test_search_multicriteria(self, service: TransactionsService) -> None:
        """Tester la recherche multi-critères."""
        request = TransactionSearchRequest(
            type='CASH_OUT',
            isFraud=1
        )
        results = service.search_transactions(request)
        
        assert all(t.type == 'CASH_OUT' for t in results)
        assert all(t.isFraud == 1 for t in results)
    
    def test_search_with_amount_range(self, service: TransactionsService) -> None:
        """Tester la recherche avec un intervalle de montant."""
        request = TransactionSearchRequest(
            amount_range=[100.0, 10000.0]
        )
        results = service.search_transactions(request)
        
        assert all(100.0 <= t.amount <= 10000.0 for t in results)
    
    def test_get_transaction_types(self, service: TransactionsService) -> None:
        """Tester la récupération des types de transactions uniques."""
        types = service.get_transaction_types()
        
        assert isinstance(types, list)
        assert len(types) > 0
        assert 'PAYMENT' in types
    
    def test_get_recent_transactions(self, service: TransactionsService) -> None:
        """Tester la récupération des transactions récentes."""
        recent = service.get_recent_transactions(n=3)
        
        assert len(recent) == 3
        assert recent[0].step >= recent[-1].step
    
    def test_delete_transaction(self, service: TransactionsService) -> None:
        """Tester la suppression d’une transaction."""
        deleted = service.delete_transaction('tx_0')
        
        assert deleted is True
    
    def test_delete_nonexistent_transaction(self, service: TransactionsService) -> None:
        """Tester la suppression d’une transaction inexistante."""
        deleted = service.delete_transaction('tx_9999')
        
        assert deleted is False
    
    def test_get_transactions_by_customer(self, service: TransactionsService) -> None:
        """Tester la récupération des transactions par client émetteur."""
        transactions = service.get_transactions_by_customer('C001')
        
        assert all(t.nameOrig == 'C001' for t in transactions)
        assert len(transactions) == 2
    
    def test_get_transactions_to_customer(self, service: TransactionsService) -> None:
        """Tester la récupération des transactions vers un client destinataire."""
        transactions = service.get_transactions_to_customer('C001')
        
        assert all(t.nameDest == 'C001' for t in transactions)
        assert len(transactions) == 0