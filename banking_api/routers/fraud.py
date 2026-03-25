"""
Fraud Router.

Exposes endpoints 13–15 for fraud analysis and prediction.
"""

from fastapi import APIRouter

from banking_api.models.schemas import (
    FraudByType,
    FraudPredictRequest,
    FraudPredictResponse,
    FraudSummary,
)
from banking_api.services import fraud_detection_service as svc

router: APIRouter = APIRouter()


@router.get("/summary", response_model=FraudSummary, summary="Fraud overview")
def get_fraud_summary() -> FraudSummary:
    """Return a global overview of fraud in the dataset.

    Returns
    -------
    FraudSummary
        Total frauds, flagged transactions, precision and recall.
    """
    return svc.get_fraud_summary()


@router.get(
    "/by-type",
    response_model=list[FraudByType],
    summary="Fraud rate by type",
)
def get_fraud_by_type() -> list[FraudByType]:
    """Return the fraud rate broken down by transaction type.

    Returns
    -------
    list[FraudByType]
        One entry per transaction type with fraud counts and rate.
    """
    return svc.get_fraud_by_type()


@router.post(
    "/predict",
    response_model=FraudPredictResponse,
    summary="Fraud prediction",
)
def predict_fraud(request: FraudPredictRequest) -> FraudPredictResponse:
    """Score a transaction to estimate its probability of being fraudulent.

    Parameters
    ----------
    request : FraudPredictRequest
        Transaction features: type, amount, original and new balance.

    Returns
    -------
    FraudPredictResponse
        Boolean fraud flag and probability score.
    """
    return svc.predict_fraud(request)
