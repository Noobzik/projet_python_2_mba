"""Fraud detection routes.

This module defines API endpoints for fraud detection and analysis.
"""

from typing import List
from fastapi import APIRouter
from ..models.stats import FraudSummary, FraudByType
from ..models.transaction import FraudPredictionRequest, FraudPredictionResponse
from ..services.fraud_detection_service import FraudDetectionService

router = APIRouter(prefix="/api/fraud", tags=["fraud"])
service = FraudDetectionService()


@router.get("/summary", response_model=FraudSummary)
def get_fraud_summary() -> FraudSummary:
    """Get fraud detection summary.

    Returns
    -------
    FraudSummary
        Summary of fraud statistics including total frauds,
        flagged count, and fraud rate.
    """
    return service.get_fraud_summary()


@router.get("/by-type", response_model=List[FraudByType])
def get_fraud_by_type() -> List[FraudByType]:
    """Get fraud statistics by transaction type.

    Returns
    -------
    List[FraudByType]
        List of fraud rates and counts for each transaction type.
    """
    return service.get_fraud_by_type()


@router.post("/predict", response_model=FraudPredictionResponse)
def predict_fraud(request: FraudPredictionRequest) -> FraudPredictionResponse:
    """Predict if a transaction is fraudulent.

    This endpoint uses a simplified rule-based model.
    In production, this would use a trained ML model.

    Parameters
    ----------
    request : FraudPredictionRequest
        Transaction data for fraud prediction.

    Returns
    -------
    FraudPredictionResponse
        Prediction result with fraud probability.
    """
    return service.predict_fraud(request)
