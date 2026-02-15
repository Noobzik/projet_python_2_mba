"""Tests pour le service de détection de fraude."""

from banking_api.services import fraud_detection_service


class TestFraudPrediction:
    """Tests pour la fonction predict_fraud."""

    def test_predict_fraud_high_amount(self):
        """Test : montant très élevé devrait être détecté comme fraude."""
        result = fraud_detection_service.predict_fraud(
            transaction_type="Online Transaction",
            amount=15000.0,
            merchant_city="New York",
            merchant_state="NY",
        )

        # Vérifications
        assert result["isFraud"] is True
        assert result["probability"] >= 0.5
        assert len(result["reasons"]) > 0
        assert "Montant très élevé" in result["reasons"]

    def test_predict_fraud_normal_amount(self):
        """Test : montant normal ne devrait PAS être fraude."""
        result = fraud_detection_service.predict_fraud(
            transaction_type="Chip Transaction",
            amount=50.0,
            merchant_city="Paris",
            merchant_state="FR",
        )

        # Vérifications
        assert result["isFraud"] is False
        assert result["probability"] < 0.5
        assert result["reasons"] == ["Transaction normale"]

    def test_predict_fraud_negative_amount(self):
        """Test : montant négatif devrait être fraude."""
        result = fraud_detection_service.predict_fraud(
            transaction_type="Swipe Transaction",
            amount=-100.0,
            merchant_city="London",
            merchant_state="UK",
        )

        assert result["isFraud"] is True
        assert "Montant négatif détecté" in result["reasons"]

    def test_predict_fraud_very_low_amount(self):
        """Test : montant très faible (test de carte volée)."""
        result = fraud_detection_service.predict_fraud(
            transaction_type="Online Transaction",
            amount=0.5,
            merchant_city="Madrid",
            merchant_state="ES",
        )

        # Montant très faible ajoute +0.1 de probabilité
        assert result["probability"] >= 0.1


class TestFraudSummary:
    """Tests pour get_fraud_summary."""

    def test_get_fraud_summary_structure(self):
        """Test : la structure du résumé est correcte."""
        result = fraud_detection_service.get_fraud_summary()

        # Vérifier que toutes les clés sont présentes
        assert "total_frauds" in result
        assert "flagged" in result
        assert "precision" in result
        assert "recall" in result

        # Vérifier les types
        assert isinstance(result["total_frauds"], int)
        assert isinstance(result["flagged"], int)
        assert isinstance(result["precision"], float)
        assert isinstance(result["recall"], float)

    def test_get_fraud_summary_values(self):
        """Test : les valeurs sont cohérentes."""
        result = fraud_detection_service.get_fraud_summary()

        # Valeurs logiques
        assert result["total_frauds"] >= 0
        assert result["flagged"] >= 0
        assert 0.0 <= result["precision"] <= 1.0
        assert 0.0 <= result["recall"] <= 1.0


class TestFraudByType:
    """Tests pour get_fraud_by_type."""

    def test_get_fraud_by_type_structure(self):
        """Test : la structure du résultat est correcte."""
        result = fraud_detection_service.get_fraud_by_type()

        # Devrait retourner une liste
        assert isinstance(result, list)
        assert len(result) > 0

        # Vérifier la structure du premier élément
        first_item = result[0]
        assert "type" in first_item
        assert "total_transactions" in first_item
        assert "fraud_count" in first_item
        assert "fraud_rate" in first_item

    def test_get_fraud_by_type_values(self):
        """Test : les valeurs sont cohérentes."""
        result = fraud_detection_service.get_fraud_by_type()

        for item in result:
            # Valeurs logiques
            assert item["total_transactions"] > 0
            assert item["fraud_count"] >= 0
            assert 0.0 <= item["fraud_rate"] <= 100.0

            # Le nombre de fraudes ne peut pas dépasser le total
            assert item["fraud_count"] <= item["total_transactions"]
