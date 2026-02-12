"""Tests fonctionnels pour les routes de détection de fraude.

Ce module teste les endpoints API de détection de fraude (Routes 13-15).
"""
import unittest
from fastapi.testclient import TestClient
from banking_api.main import app


class TestFraudRoutes(unittest.TestCase):
    """Suite de tests pour les routes de détection de fraude."""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Initialiser le client de test pour tous les tests."""
        cls.client = TestClient(app)
    
    def test_get_fraud_summary(self) -> None:
        """Tester GET /api/fraud/summary."""
        response = self.client.get("/api/fraud/summary")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_frauds', data)
        self.assertIn('flagged', data)
        self.assertIn('fraud_rate', data)
        self.assertIn('detection_rate', data)
    
    def test_fraud_summary_values(self) -> None:
        """Tester que le résumé de fraude contient des valeurs valides."""
        response = self.client.get("/api/fraud/summary")
        data = response.json()
        
        self.assertGreaterEqual(data['total_frauds'], 0)
        self.assertGreaterEqual(data['flagged'], 0)
        self.assertGreaterEqual(data['fraud_rate'], 0)
        self.assertLessEqual(data['fraud_rate'], 1)
    
    def test_get_fraud_by_type(self) -> None:
        """Tester GET /api/fraud/by-type."""
        response = self.client.get("/api/fraud/by-type")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_fraud_by_type_structure(self) -> None:
        """Tester la structure des données de fraude par type."""
        response = self.client.get("/api/fraud/by-type")
        data = response.json()
        
        for fraud_stat in data:
            self.assertIn('type', fraud_stat)
            self.assertIn('fraud_count', fraud_stat)
            self.assertIn('total_count', fraud_stat)
            self.assertIn('fraud_rate', fraud_stat)
    
    def test_post_fraud_predict(self) -> None:
        """Tester POST /api/fraud/predict."""
        prediction_data = {
            "type": "TRANSFER",
            "amount": 5000.0,
            "oldbalanceOrg": 10000.0,
            "newbalanceOrig": 5000.0
        }
        response = self.client.post("/api/fraud/predict", json=prediction_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('isFraud', data)
        self.assertIn('probability', data)
        self.assertIn('risk_level', data)
    
    def test_fraud_predict_high_risk(self) -> None:
        """Tester la prédiction de fraude pour une transaction à haut risque."""
        prediction_data = {
            "type": "CASH_OUT",
            "amount": 250000.0,
            "oldbalanceOrg": 300000.0,
            "newbalanceOrig": 0.0
        }
        response = self.client.post("/api/fraud/predict", json=prediction_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data['isFraud'], bool)
        self.assertGreaterEqual(data['probability'], 0)
        self.assertLessEqual(data['probability'], 1)
    
    def test_fraud_predict_low_risk(self) -> None:
        """Tester la prédiction de fraude pour une transaction à faible risque."""
        prediction_data = {
            "type": "PAYMENT",
            "amount": 50.0,
            "oldbalanceOrg": 10000.0,
            "newbalanceOrig": 9950.0
        }
        response = self.client.post("/api/fraud/predict", json=prediction_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data['risk_level'], ['LOW', 'MEDIUM', 'HIGH'])
    
    def test_fraud_predict_invalid_data(self) -> None:
        """Tester la prédiction de fraude avec des données invalides."""
        prediction_data = {
            "type": "TRANSFER",
            "amount": -100.0,
            "oldbalanceOrg": 10000.0,
            "newbalanceOrig": 5000.0
        }
        response = self.client.post("/api/fraud/predict", json=prediction_data)
        
        self.assertIn(response.status_code, [422, 400])


if __name__ == '__main__':
    unittest.main()