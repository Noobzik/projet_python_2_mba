from __future__ import annotations

import pandas as pd

from banking_api.models.stats import (
    AmountDistributionBucket,
    AmountDistributionOut,
    ByTypeItem,
    ByTypeOut,
    DailyItem,
    DailyOut,
    StatsOverviewOut,
)
from banking_api.services.dataset_loader import get_dataset
from banking_api.services.transactions_service import _exclude_deleted


def stats_overview() -> StatsOverviewOut:
    df = get_dataset()
    df = _exclude_deleted(df)

    required = {"type", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    total = int(df.shape[0])
    avg_amount = float(pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).mean())

    most_common_type = None
    if total > 0:
        most_common_type = (
            df["type"].dropna().astype(str).value_counts().idxmax()
            if "type" in df.columns
            else None
        )

    fraud_rate = 0.0
    if "isFraud" in df.columns and total > 0:
        fraud_col = pd.to_numeric(df["isFraud"], errors="coerce").fillna(0).astype(int)
        fraud_rate = float(fraud_col.mean())

    return StatsOverviewOut(
        total_transactions=total,
        fraud_rate=fraud_rate,
        avg_amount=avg_amount,
        most_common_type=most_common_type,
    )


def amount_distribution() -> AmountDistributionOut:
    df = get_dataset()
    df = _exclude_deleted(df)

    if "amount" not in df.columns:
        raise RuntimeError("Dataset missing required column: amount")

    amounts = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

    # Bins "safe" and readable (can be aligned later to the subject example if needed)
    bins = [0, 10, 100, 1000, 10000, float("inf")]
    labels = ["0-10", "10-100", "100-1k", "1k-10k", "10k+"]

    cats = pd.cut(amounts, bins=bins, labels=labels, right=False, include_lowest=True)
    counts = cats.value_counts().reindex(labels, fill_value=0)

    buckets = [AmountDistributionBucket(range=lab, count=int(counts[lab])) for lab in labels]
    return AmountDistributionOut(buckets=buckets)


def stats_by_type() -> ByTypeOut:
    df = get_dataset()
    df = _exclude_deleted(df)

    required = {"type", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    df = df.copy()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

    grouped = df.groupby(df["type"].astype(str))["amount"].agg(["count", "mean"]).reset_index()
    items = [
        ByTypeItem(type=str(row["type"]), count=int(row["count"]), avg_amount=float(row["mean"]))
        for _, row in grouped.iterrows()
    ]
    items.sort(key=lambda x: x.count, reverse=True)
    return ByTypeOut(items=items)


def stats_daily() -> DailyOut:
    df = get_dataset()
    df = _exclude_deleted(df)

    required = {"amount"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    if "step" not in df.columns:
        raise RuntimeError("Dataset missing required column: step (needed for daily stats)")

    df = df.copy()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["step"] = pd.to_numeric(df["step"], errors="coerce").fillna(0).astype(int)

    grouped = df.groupby("step")["amount"].agg(["count", "mean"]).reset_index()
    items = [
        DailyItem(step=int(row["step"]), count=int(row["count"]), avg_amount=float(row["mean"]))
        for _, row in grouped.iterrows()
    ]
    items.sort(key=lambda x: x.step)
    return DailyOut(items=items)
