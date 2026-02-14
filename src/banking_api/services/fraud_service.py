from __future__ import annotations

import pandas as pd

from banking_api.models.fraud import (
    FraudCustomerOut,
    FraudSummaryOut,
    FraudTopCustomersOut,
    FraudTransactionListOut,
)
from banking_api.models.transaction import TransactionOut
from banking_api.services.dataset_loader import get_dataset
from banking_api.services.transactions_service import _exclude_deleted


def _fraud_mask(df: pd.DataFrame) -> pd.Series:
    if "isFraud" not in df.columns:
        # no fraud column -> no frauds
        return pd.Series([False] * df.shape[0], index=df.index)

    col = pd.to_numeric(df["isFraud"], errors="coerce").fillna(0).astype(int)
    return col == 1


def _flagged_mask(df: pd.DataFrame) -> pd.Series:
    if "isFlaggedFraud" not in df.columns:
        return pd.Series([False] * df.shape[0], index=df.index)

    col = pd.to_numeric(df["isFlaggedFraud"], errors="coerce").fillna(0).astype(int)
    return col == 1


def fraud_summary() -> FraudSummaryOut:
    df = get_dataset()
    df = _exclude_deleted(df)

    total = int(df.shape[0])
    frauds = int(_fraud_mask(df).sum())
    flagged = int(_flagged_mask(df).sum())

    fraud_rate = float(frauds / total) if total > 0 else 0.0
    flagged_rate = float(flagged / total) if total > 0 else 0.0

    return FraudSummaryOut(
        total_transactions=total,
        total_frauds=frauds,
        flagged_frauds=flagged,
        fraud_rate=fraud_rate,
        flagged_rate=flagged_rate,
    )


def list_fraud_transactions(page: int, limit: int) -> FraudTransactionListOut:
    df = get_dataset()
    df = _exclude_deleted(df)

    required = {"type", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    fraud_df = df[_fraud_mask(df)]

    offset = (page - 1) * limit
    page_df = fraud_df.iloc[offset : offset + limit]

    transactions: list[TransactionOut] = []
    for row_index, row in page_df.iterrows():
        transactions.append(TransactionOut.from_row(int(row_index), row.to_dict()))

    return FraudTransactionListOut(page=page, transactions=transactions)


def top_fraud_customers(n: int) -> FraudTopCustomersOut:
    df = get_dataset()
    df = _exclude_deleted(df)

    if "nameOrig" not in df.columns:
        raise RuntimeError("Dataset missing required column: nameOrig")

    fraud_df = df[_fraud_mask(df)]
    counts = fraud_df["nameOrig"].dropna().astype(str).value_counts().head(n)

    customers = [FraudCustomerOut(id=str(cid), fraud_count=int(cnt)) for cid, cnt in counts.items()]
    return FraudTopCustomersOut(n=n, customers=customers)
