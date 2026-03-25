"""Unit tests for fraud_detection_service."""

import pandas as pd

from banking_api.models.schemas import FraudPredictRequest
from banking_api.services import fraud_detection_service as svc


def test_get_fraud_summary(sample_df: pd.DataFrame) -> None:
    result = svc.get_fraud_summary(df=sample_df)
    assert result.total_frauds == 1
    assert result.flagged == 1
    assert 0.0 <= result.precision <= 1.0
    assert 0.0 <= result.recall <= 1.0


def test_get_fraud_by_type(sample_df: pd.DataFrame) -> None:
    results = svc.get_fraud_by_type(df=sample_df)
    assert len(results) > 0
    for r in results:
        assert 0.0 <= r.fraud_rate <= 1.0
        assert r.fraud_count <= r.total


def test_predict_fraud_high_risk() -> None:
    req = FraudPredictRequest(
        type="TRANSFER",
        amount=500_000.0,
        oldbalanceOrg=500_000.0,
        newbalanceOrig=0.0,
    )
    result = svc.predict_fraud(req)
    assert result.isFraud is True
    assert result.probability >= 0.5


def test_predict_fraud_low_risk() -> None:
    req = FraudPredictRequest(
        type="PAYMENT",
        amount=50.0,
        oldbalanceOrg=1000.0,
        newbalanceOrig=950.0,
    )
    result = svc.predict_fraud(req)
    assert result.isFraud is False
    assert result.probability < 0.5


def test_predict_fraud_probability_bounded() -> None:
    req = FraudPredictRequest(
        type="CASH_OUT",
        amount=300_000.0,
        oldbalanceOrg=300_000.0,
        newbalanceOrig=0.0,
    )
    result = svc.predict_fraud(req)
    assert 0.0 <= result.probability <= 1.0


def test_fraud_by_type_transfer_has_fraud(sample_df: pd.DataFrame) -> None:
    results = svc.get_fraud_by_type(df=sample_df)
    transfer = next((r for r in results if r.type == "TRANSFER"), None)
    assert transfer is not None
    assert transfer.fraud_count == 1
