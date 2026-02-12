"""
Service de détection de fraude.
"""

from banking_api.models.schemas import FraudPredictionResponse


class FraudDetectionService:
    """Service simple basé sur des règles."""

    def __init__(self):
        pass

    def predict_fraud(self, request):
        """Prédire le risque de fraude."""

        probability = 0.0

        # Type à risque
        if request.type in ["TRANSFER", "CASH_OUT"]:
            probability += 0.3

        # Montant
        if request.amount >= 200000:
            probability += 0.4
        elif request.amount >= 10000:
            probability += 0.2

        # Incohérence de balance
        expected_new_balance = request.oldbalanceOrg - request.amount
        balance_diff = abs(expected_new_balance - request.newbalanceOrig)

        if balance_diff > 1000:
            probability += 0.3

        # Limite à 1.0
        probability = min(probability, 1.0)

        # Niveau de risque
        if probability < 0.3:
            risk_level = "LOW"
        elif probability < 0.7:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        is_fraud = probability >= 0.5

        return FraudPredictionResponse(
            isFraud=is_fraud,
            probability=round(probability, 2),
            risk_level=risk_level
        )
