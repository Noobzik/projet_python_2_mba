"""Fraud detection service layer.

This module provides business logic for fraud detection and analysis.
"""

from typing import Dict, List
import pandas as pd
from ..models.stats import FraudSummary, FraudByType
from ..models.transaction import FraudPredictionRequest, FraudPredictionResponse
from ..utils.data_loader import DataLoader


class FraudDetectionService:
    """Service for fraud detection operations.

    This service handles fraud analysis and simple fraud prediction.
    """

    def __init__(self) -> None:
        """Initialize the fraud detection service."""
        self.data_loader = DataLoader()

    def get_fraud_summary(self) -> FraudSummary:
        """Get summary of fraud statistics.

        Returns
        -------
        FraudSummary
            Summary including total frauds, flagged count, and fraud rate.
        """
        df = self.data_loader.get_data()

        # Parse amount if needed - use vectorized operations
        if df['amount'].dtype == 'object':
            amounts = df['amount'].str.replace('$', '').str.replace(',', '').astype(float)
        else:
            amounts = df['amount']

        total_transactions = len(df)
        total_frauds = int(df['isFraud'].sum())
        flagged = total_frauds
        fraud_rate = total_frauds / total_transactions if total_transactions > 0 else 0.0

        # Calculate fraud amount using boolean indexing
        fraud_mask = df['isFraud'] == 1
        total_fraud_amount = float(amounts[fraud_mask].sum()) if fraud_mask.any() else 0.0

        # Handle NaN
        if pd.isna(total_fraud_amount):
            total_fraud_amount = 0.0

        return FraudSummary(
            total_frauds=total_frauds,
            flagged=flagged,
            fraud_rate=float(fraud_rate),
            total_fraud_amount=total_fraud_amount
        )

    def get_fraud_by_type(self) -> List[FraudByType]:
        """Get fraud statistics by transaction method (use_chip).

        Returns
        -------
        List[FraudByType]
            List of fraud statistics for each transaction method.
        """
        df = self.data_loader.get_data()

        # Use vectorized groupby for better performance
        grouped = df.groupby('use_chip', dropna=True).agg({
            'isFraud': ['sum', 'count']
        }).reset_index()

        grouped.columns = ['type', 'fraud_count', 'total_count']

        fraud_stats = []
        for _, row in grouped.iterrows():
            fraud_rate = row['fraud_count'] / row['total_count'] if row['total_count'] > 0 else 0.0

            fraud_stats.append(FraudByType(
                type=str(row['type']),
                fraud_rate=float(fraud_rate),
                fraud_count=int(row['fraud_count']),
                total_count=int(row['total_count'])
            ))

        return sorted(fraud_stats, key=lambda x: x.fraud_rate, reverse=True)

    def predict_fraud(
        self,
        request: FraudPredictionRequest
    ) -> FraudPredictionResponse:
        """Predict if a transaction is fraudulent.

        This is a simplified rule-based prediction model.
        In production, this would use a trained ML model.

        Parameters
        ----------
        request : FraudPredictionRequest
            Transaction data for prediction.

        Returns
        -------
        FraudPredictionResponse
            Prediction result with probability.

        Notes
        -----
        This implementation uses simple heuristics:
        - Online/Chip transactions are riskier
        - High amounts are suspicious
        - Certain merchant categories
        - Certain states have higher fraud rates
        """
        score = 0.0

        # Transaction method risk
        if 'Online' in request.use_chip:
            score += 0.3
        elif 'Chip' in request.use_chip:
            score += 0.1

        # High amount risk
        if request.amount > 1000:
            score += 0.3
        if request.amount > 5000:
            score += 0.2

        # Certain MCC codes are riskier (example: 5999 - miscellaneous)
        risky_mcc = [5999, 5815, 5962, 5912]
        if request.mcc in risky_mcc:
            score += 0.2

        # Certain states have higher fraud (example heuristic)
        risky_states = ['CA', 'FL', 'NY', 'TX']
        if request.merchant_state in risky_states:
            score += 0.1

        probability = min(score, 1.0)
        is_fraud = probability > 0.5

        return FraudPredictionResponse(
            isFraud=is_fraud,
            probability=probability
        )
