"""Tests unitaires pour le service de détection de fraude.

Ce module teste la classe FraudDetectionService.
"""
import pytest
from pathlib import Path
from banking_api.services.fraud_detection_service import FraudDetectionService
from banking_api.models.schemas import FraudPredictionRequest
from banking_api.utils.data_loader import DataLoader


@pytest.fixture
def service(temp_csv_file: Path) -> FraudDetectionService:
    """Créer une instance de FraudDetectionService avec des données de test."""
    loader = DataLoader()
    loader.load_data(temp_csv_file)
    return FraudDetectionService()


class TestFraudDetectionService:
    """Suite de tests pour FraudDetectionService."""
    
    def test_get_fraud_summary(self, service: FraudDetectionService) -> None:
        """Tester les statistiques récapitulatives de fraude."""
        summary = service.get_fraud_summary()
        
        assert summary.total_frauds == 3
        assert summary.flagged == 0
        assert 0 <= summary.fraud_rate <= 1
        assert 0 <= summary.detection_rate <= 1
    
    def test_fraud_summary_rates(self, service: FraudDetectionService) -> None:
        """Tester les calculs des taux de fraude."""
        summary = service.get_fraud_summary()
        
        expected_fraud_rate = 3 / 10
        assert abs(summary.fraud_rate - expected_fraud_rate) < 0.01
    
    def test_get_fraud_by_type(self, service: FraudDetectionService) -> None:
        """Tester les statistiques de fraude par type de transaction."""
        fraud_by_type = service.get_fraud_by_type()
        
        assert len(fraud_by_type) > 0
        assert all(f.fraud_count >= 0 for f in fraud_by_type)
        assert all(f.total_count > 0 for f in fraud_by_type)
        assert all(0 <= f.fraud_rate <= 1 for f in fraud_by_type)
    
    def test_fraud_by_type_sorted(self, service: FraudDetectionService) -> None:
        """Tester que les fraudes par type sont triées par taux de fraude décroissant."""
        fraud_by_type = service.get_fraud_by_type()
        
        fraud_rates = [f.fraud_rate for f in fraud_by_type]
        assert fraud_rates == sorted(fraud_rates, reverse=True)
    
    def test_predict_fraud_high_risk(self, service: FraudDetectionService) -> None:
        """Tester la prédiction de fraude pour une transaction à haut risque."""
        request = FraudPredictionRequest(
            type='CASH_OUT',
            amount=250000.0,
            oldbalanceOrg=300000.0,
            newbalanceOrig=0.0
        )
        
        prediction = service.predict_fraud(request)
        
        assert isinstance(prediction.isFraud, bool)
        assert 0 <= prediction.probability <= 1
        assert prediction.risk_level in ['LOW', 'MEDIUM', 'HIGH']
    
    def test_predict_fraud_low_risk(self, service: FraudDetectionService) -> None:
        """Tester la prédiction de fraude pour une transaction à faible risque."""
        request = FraudPredictionRequest(
            type='PAYMENT',
            amount=50.0,
            oldbalanceOrg=10000.0,
            newbalanceOrig=9950.0
        )
        
        prediction = service.predict_fraud(request)
        
        assert prediction.probability < 0.5
        assert prediction.risk_level == 'LOW'
    
    def test_predict_fraud_transfer_type(self, service: FraudDetectionService) -> None:
        """Tester que la prédiction de fraude prend en compte le type de transaction."""
        request = FraudPredictionRequest(
            type='TRANSFER',
            amount=5000.0,
            oldbalanceOrg=10000.0,
            newbalanceOrig=5000.0
        )
        
        prediction = service.predict_fraud(request)
        
        assert prediction.probability > 0
    
    def test_predict_fraud_high_amount(self, service: FraudDetectionService) -> None:
        """Tester la prédiction de fraude pour une transaction avec un montant élevé."""
        request = FraudPredictionRequest(
            type='TRANSFER',
            amount=300000.0,
            oldbalanceOrg=350000.0,
            newbalanceOrig=50000.0
        )
        
        prediction = service.predict_fraud(request)
        
        assert prediction.probability >= 0.5
        assert prediction.risk_level in ['MEDIUM', 'HIGH']
    
    def test_predict_fraud_probability_range(self, service: FraudDetectionService) -> None:
        """Tester que la probabilité de fraude est dans un intervalle valide."""
        request = FraudPredictionRequest(
            type='CASH_OUT',
            amount=500000.0,
            oldbalanceOrg=500000.0,
            newbalanceOrig=0.0
        )
        
        prediction = service.predict_fraud(request)
        
        assert 0.0 <= prediction.probability <= 1.0