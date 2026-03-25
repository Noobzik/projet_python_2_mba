"""
Fraud Detection Service.

Provides fraud rate analytics and a lightweight rule-based scoring model
for the ``POST /api/fraud/predict`` endpoint.

Notes
-----
The scoring model is intentionally simple (heuristic rules) so that the
service has no external model dependency and no training data requirement.
A production system would replace ``predict_fraud`` with a proper ML model.
"""

from typing import Optional
import pandas as pd

from banking_api.models.schemas import (
    FraudByType,
    FraudPredictRequest,
    FraudPredictResponse,
    FraudSummary,
)
from banking_api.services.data_loader import DataLoader


def _get_df(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Return provided DataFrame or singleton dataset.

    Parameters
    ----------
    df : pd.DataFrame or None
        Caller-supplied DataFrame (tests) or ``None``.

    Returns
    -------
    pd.DataFrame
        Active dataset.
    """
    return df if df is not None else DataLoader.get_instance().df


def get_fraud_summary(df: Optional[pd.DataFrame] = None) -> FraudSummary:
    """Compute a global fraud overview.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    FraudSummary
        Total fraudulent transactions, flagged count, precision and recall.
    """
    data: pd.DataFrame = _get_df(df)

    total_frauds: int = int(data["isFraud"].sum())
    flagged: int = int(data["isFlaggedFraud"].sum())

    # Simplified precision / recall derived from isFraud vs isFlaggedFraud
    true_positives: int = int(
        ((data["isFraud"] == 1) & (data["isFlaggedFraud"] == 1)).sum()
    )
    precision: float = (
        true_positives / flagged if flagged else 0.0
    )
    recall: float = (
        true_positives / total_frauds if total_frauds else 0.0
    )

    return FraudSummary(
        total_frauds=total_frauds,
        flagged=flagged,
        precision=round(precision, 4),
        recall=round(recall, 4),
    )


def get_fraud_by_type(
    df: Optional[pd.DataFrame] = None,
) -> list[FraudByType]:
    """Return the fraud rate for each transaction type.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[FraudByType]
        One entry per transaction type.
    """
    data: pd.DataFrame = _get_df(df)
    grouped: pd.DataFrame = (
        data.groupby("type")
        .agg(total=("isFraud", "count"), fraud_count=("isFraud", "sum"))
        .reset_index()
    )
    result: list[FraudByType] = []
    for _, row in grouped.iterrows():
        total: int = int(row["total"])
        fraud_count: int = int(row["fraud_count"])
        result.append(
            FraudByType(
                type=str(row["type"]),
                total=total,
                fraud_count=fraud_count,
                fraud_rate=round(fraud_count / total if total else 0.0, 6),
            )
        )
    return result


def predict_fraud(request: FraudPredictRequest) -> FraudPredictResponse:
    """Score a transaction using heuristic rules.

    The scoring is based on three observable signals:

    1. Balance drop equals the transaction amount (no recipient credit).
    2. Transaction type is TRANSFER or CASH_OUT (high-risk types).
    3. Amount exceeds 200 000 monetary units (large transactions).

    Each signal contributes equally to a probability score.

    Parameters
    ----------
    request : FraudPredictRequest
        Input features for the transaction to score.

    Returns
    -------
    FraudPredictResponse
        Boolean fraud flag and estimated probability.
    """
    score: float = 0.0

    balance_drop: float = request.oldbalanceOrg - request.newbalanceOrig
    if abs(balance_drop - request.amount) < 1.0:
        score += 0.40

    if request.type in {"TRANSFER", "CASH_OUT"}:
        score += 0.35

    if request.amount > 200_000:
        score += 0.25

    probability: float = min(round(score, 2), 1.0)
    return FraudPredictResponse(
        isFraud=probability >= 0.50,
        probability=probability,
    )
