"""Tests pour les fonctions utilitaires."""

from banking_api.services.transactions_service import _convert_transaction_types


def test_convert_transaction_types():
    """Test de conversion des types de transaction."""
    transaction_input = {
        "id": "12345",
        "date": "2023-01-15",
        "client_id": "456",
        "card_id": "789",
        "amount": "$100.50",
        "use_chip": "Chip Transaction",
        "merchant_id": "999",
        "merchant_city": "New York",
        "merchant_state": "NY",
        "zip": "10001",
        "mcc": "5411",
        "errors": "",
    }

    result = _convert_transaction_types(transaction_input)

    assert isinstance(result["id"], int)
    assert result["id"] == 12345
    assert isinstance(result["date"], str)
    assert result["date"] == "2023-01-15"
    assert isinstance(result["client_id"], int)
    assert result["client_id"] == 456
    assert isinstance(result["amount"], float)
    assert result["amount"] == 100.50
    assert isinstance(result["use_chip"], str)
    assert result["use_chip"] == "Chip Transaction"
    assert isinstance(result["isFraud"], int)
    assert result["isFraud"] == 0


def test_fraud_prediction_zero_balance():
    """Test de prédiction avec solde zéro."""
    from banking_api.services.fraud_detection_service import predict_fraud

    prediction = predict_fraud(
        transaction_type="Online Transaction",
        amount=1000.0,
        merchant_city="New York",
        merchant_state="NY",
    )

    assert "isFraud" in prediction
    assert "probability" in prediction
    assert "reasons" in prediction


def test_fraud_prediction_normal_transaction():
    """Test de prédiction pour une transaction normale."""
    from banking_api.services.fraud_detection_service import predict_fraud

    prediction = predict_fraud(
        transaction_type="Chip Transaction",
        amount=50.0,
        merchant_city="Paris",
        merchant_state="FR",
    )

    assert "isFraud" in prediction
    assert "probability" in prediction
    assert "reasons" in prediction
    assert isinstance(prediction["isFraud"], bool)
