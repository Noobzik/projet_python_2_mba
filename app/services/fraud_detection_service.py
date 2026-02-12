"""
Fraud detection service for Banking Transactions API.

This module provides fraud analysis and simple prediction scoring.
"""

from typing import List, Dict, Any
from collections import Counter
from app.utils.loader import load_transactions
from app.models.schemas import (
    FraudSummary,
    FraudByType,
    FraudPredictionRequest,
    FraudPredictionResponse,
)

_TRANSACTIONS: List[Dict[str, Any]] | None = None


def _get_data() -> List[Dict[str, Any]]:
    """
    Get cached transaction data.

    Returns
    -------
    List[Dict[str, Any]]
        List of transaction dictionaries
    """
    global _TRANSACTIONS
    if _TRANSACTIONS is None:
        _TRANSACTIONS = load_transactions()
    return _TRANSACTIONS


def get_fraud_summary() -> FraudSummary:
    """
    Calculate fraud detection summary statistics.

    Returns
    -------
    FraudSummary
        Summary of fraud metrics including precision and recall
    """
    data = _get_data()

    total_frauds = sum(1 for t in data if int(t.get("isFraud", 0)) == 1)
    flagged = sum(1 for t in data if int(t.get("isFlaggedFraud", 0)) == 1)

    # Calculate precision and recall
    # True Positives: both isFraud and isFlaggedFraud are 1
    tp = sum(
        1 for t in data
        if int(t.get("isFraud", 0)) == 1 and int(t.get("isFlaggedFraud", 0)) == 1
    )

    # False Positives: isFlaggedFraud is 1 but isFraud is 0
    fp = sum(
        1 for t in data
        if int(t.get("isFraud", 0)) == 0 and int(t.get("isFlaggedFraud", 0)) == 1
    )

    # False Negatives: isFraud is 1 but isFlaggedFraud is 0
    fn = sum(
        1 for t in data
        if int(t.get("isFraud", 0)) == 1 and int(t.get("isFlaggedFraud", 0)) == 0
    )

    # Precision = TP / (TP + FP)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

    # Recall = TP / (TP + FN)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    return FraudSummary(
        total_frauds=total_frauds,
        flagged=flagged,
        precision=round(precision, 2),
        recall=round(recall, 2),
    )


def get_fraud_by_type() -> List[FraudByType]:
    """
    Calculate fraud rate by transaction type.

    Returns
    -------
    List[FraudByType]
        Fraud statistics for each transaction type
    """
    data = _get_data()

    if len(data) == 0:
        return []

    fraud_stats = []
    
    # Group by type
    types = set(t.get("type") for t in data if t.get("type"))
    
    for tx_type in types:
        # All transactions of this type
        type_txs = [t for t in data if t.get("type") == tx_type]
        total_count = len(type_txs)
        
        # Fraudulent transactions of this type
        fraud_count = sum(1 for t in type_txs if int(t.get("isFraud", 0)) == 1)
        
        # Fraud rate
        fraud_rate = (fraud_count / total_count) if total_count > 0 else 0.0

        fraud_stats.append(
            FraudByType(
                type=tx_type,
                total_count=total_count,
                fraud_count=fraud_count,
                fraud_rate=round(fraud_rate, 4),
            )
        )

    # Sort by fraud rate descending
    fraud_stats.sort(key=lambda x: x.fraud_rate, reverse=True)
    return fraud_stats


def predict_fraud(request: FraudPredictionRequest) -> FraudPredictionResponse:
    """
    Predict if a transaction is fraudulent using simple rule-based scoring.

    This is a simplified fraud detection model based on common patterns.
    In production, this would use a trained ML model.

    Parameters
    ----------
    request : FraudPredictionRequest
        Transaction details for prediction

    Returns
    -------
    FraudPredictionResponse
        Fraud prediction and probability score
    """
    data = _get_data()

    # Initialize risk score
    risk_score = 0.0

    # Rule 1: High amount transfers are riskier
    if request.type in ["TRANSFER", "CASH_OUT"] and request.amount > 200000:
        risk_score += 0.3

    # Rule 2: Balance discrepancy (amount doesn't match balance change)
    expected_new_balance = request.oldbalanceOrg - request.amount
    balance_diff = abs(expected_new_balance - request.newbalanceOrig)

    if balance_diff > request.amount * 0.1:  # 10% discrepancy
        risk_score += 0.25

    # Rule 3: Complete balance drain
    if request.newbalanceOrig == 0 and request.oldbalanceOrg > 0:
        risk_score += 0.2

    # Rule 4: Very large amounts
    if request.amount > 500000:
        risk_score += 0.15

    # Rule 5: Check historical fraud rate for this type
    if len(data) > 0:
        type_txs = [t for t in data if t.get("type") == request.type]
        if len(type_txs) > 0:
            type_fraud_rate = sum(1 for t in type_txs if int(t.get("isFraud", 0)) == 1) / len(type_txs)
            risk_score += type_fraud_rate * 0.1

    # Cap probability at 1.0
    probability = min(risk_score, 1.0)

    # Threshold for classification
    is_fraud = probability > 0.5

    return FraudPredictionResponse(
        isFraud=is_fraud,
        probability=round(probability, 2)
    )