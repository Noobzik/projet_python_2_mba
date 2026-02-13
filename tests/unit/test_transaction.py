"""Tests unitaires pour le modèle Transaction.

Ce module teste les validations du modèle Transaction.
"""

import pytest
from pydantic import ValidationError

from banking_api.models.transaction import Transaction


class TestTransactionValidation:
    """Tests pour les validations de Transaction."""

    def test_transaction_invalid_type_validation(self) -> None:
        """Tester la validation du type de transaction invalide.

        Couvre la ligne 74 de transaction.py : raise ValueError("Invalid transaction type")
        """
        # Essayer de créer une transaction avec un type invalide
        with pytest.raises(ValidationError) as exc_info:
            Transaction(
                step=1,
                type="INVALID_TYPE",  # Type non autorisé - déclenche ligne 74
                amount=100.0,
                nameOrig="Alice",
                oldbalanceOrg=500.0,
                newbalanceOrig=400.0,
                nameDest="Bob",
                oldbalanceDest=200.0,
                newbalanceDest=300.0,
                isFraud=0,
                isFlaggedFraud=0,
            )

        # Vérifier que l'erreur contient le message de la ligne 74
        assert "Invalid transaction type" in str(exc_info.value)

    def test_transaction_valid_types(self) -> None:
        """Tester que les types valides sont acceptés."""
        valid_types = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]

        for transaction_type in valid_types:
            # Ne devrait pas lever d'exception
            transaction = Transaction(
                step=1,
                type=transaction_type,
                amount=100.0,
                nameOrig="Alice",
                oldbalanceOrg=500.0,
                newbalanceOrig=400.0,
                nameDest="Bob",
                oldbalanceDest=200.0,
                newbalanceDest=300.0,
                isFraud=0,
                isFlaggedFraud=0,
            )
            assert transaction.type == transaction_type
