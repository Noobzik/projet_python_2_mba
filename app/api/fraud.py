"""
Fraud detection router for Banking Transactions API.

This module defines the API endpoints for fraud analysis and prediction.
"""

from fastapi import APIRouter
from typing import List
from app.models.schemas import (
    FraudSummary,
    FraudByType,
    FraudPredictionRequest,
    FraudPredictionResponse,
)
from app.services.fraud_detection_service import (
    get_fraud_summary,
    get_fraud_by_type,
    predict_fraud,
)

router = APIRouter(tags=["Fraud Detection"])


# 13️⃣ GET /api/fraud/summary
@router.get("/fraud/summary", response_model=FraudSummary)
def summary() -> FraudSummary:
    """
    Get fraud detection overview.

    Returns
    -------
    FraudSummary
        Fraud detection metrics including:
        - Total number of fraudulent transactions
        - Number of flagged transactions
        - Precision score
        - Recall score
    """
    return get_fraud_summary()


# 14️⃣ GET /api/fraud/by-type
@router.get("/fraud/by-type", response_model=List[FraudByType])
def by_type() -> List[FraudByType]:
    """
    Get fraud rate distribution by transaction type.

    Returns
    -------
    List[FraudByType]
        Fraud statistics for each transaction type including:
        - Total transaction count
        - Fraudulent transaction count
        - Fraud rate (percentage)
    """
    return get_fraud_by_type()


# 15️⃣ POST /api/fraud/predict
@router.post("/fraud/predict", response_model=FraudPredictionResponse)
def predict(request: FraudPredictionRequest) -> FraudPredictionResponse:
    """
    Predict if a transaction is fraudulent.

    This endpoint uses a simple rule-based scoring system to assess
    the likelihood of fraud based on transaction characteristics.

    Parameters
    ----------
    request : FraudPredictionRequest
        Transaction details including:
        - type: Transaction type
        - amount: Transaction amount
        - oldbalanceOrg: Origin account balance before
        - newbalanceOrig: Origin account balance after

    Returns
    -------
    FraudPredictionResponse
        Prediction result including:
        - isFraud: Boolean prediction
        - probability: Fraud probability score (0-1)
    """
    return predict_fraud(request)