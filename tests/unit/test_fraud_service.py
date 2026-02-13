"""Tests unitaires pour le service de détection de fraude.

Ce module teste la classe FraudDetectionService.
"""
import pytest
from banking_api.services.fraud_detection_service import FraudDetectionService


class TestFraudDetectionService:
    """Suite de tests pour FraudDetectionService."""
    
    def test_fraud_detection_low_risk_level(self):
        service = FraudDetectionService()
        
        class MockRequest:
            def __init__(self):
                self.type = "PAYMENT"
                self.amount = 500.0
                self.oldbalanceOrg = 1000.0
                self.newbalanceOrig = 500.0
        
        result = service.predict_fraud(MockRequest())
        
        assert result.risk_level == "LOW"
        assert result.probability == 0.0
        assert result.isFraud is False
    
    
    def test_fraud_detection_medium_risk_level(self):
        service = FraudDetectionService()
        
        class MockRequest:
            def __init__(self):
                self.type = "TRANSFER"
                self.amount = 15000.0
                self.oldbalanceOrg = 20000.0
                self.newbalanceOrig = 5000.0
        
        result = service.predict_fraud(MockRequest())
        
        assert result.probability == 0.3
        assert result.risk_level == "LOW"
        assert result.isFraud is False
    
    
    def test_fraud_detection_high_risk_level(self):
        service = FraudDetectionService()
        
        class MockRequest:
            def __init__(self):
                self.type = "CASH_OUT"
                self.amount = 250000.0
                self.oldbalanceOrg = 300000.0
                self.newbalanceOrig = 50000.0
        
        result = service.predict_fraud(MockRequest())
        
        assert result.probability == 0.7
        assert result.risk_level == "HIGH"
        assert result.isFraud is True
    
    
    def test_probability_capped_at_one(self):
        service = FraudDetectionService()
        
        class MockRequest:
            def __init__(self):
                self.type = "TRANSFER"
                self.amount = 300000.0
                self.oldbalanceOrg = 10000.0
                self.newbalanceOrig = 0.0
        
        result = service.predict_fraud(MockRequest())
        
        assert result.probability == 1.0
        assert result.risk_level == "HIGH"
        assert result.isFraud is True
    
    
    def test_fraud_detection_medium_risk_branch(self):
        """Test pour couvrir la branche MEDIUM"""
        service = FraudDetectionService()

        class MockRequest:
            def __init__(self):
                self.type = "TRANSFER"      # +0.3
                self.amount = 1000.0
                self.oldbalanceOrg = 5000.0
                self.newbalanceOrig = 2500.0  # évite vidage, force incohérence >1000

        result = service.predict_fraud(MockRequest())

        # 0.3 (type) + 0.3 (incohérence) = 0.6
        assert result.probability == 0.6
        assert result.risk_level == "MEDIUM"
        assert result.isFraud is True
