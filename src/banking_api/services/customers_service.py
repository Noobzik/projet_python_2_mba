from __future__ import annotations

import pandas as pd

from banking_api.models.customer import CustomerOut, CustomerProfileOut, TopCustomersOut
from banking_api.services.dataset_loader import get_dataset
from banking_api.services.transactions_service import _exclude_deleted


def list_customers(page: int, limit: int) -> list[CustomerOut]:
    df = get_dataset()
    df = _exclude_deleted(df)

    if "nameOrig" not in df.columns:
        raise RuntimeError("Dataset missing required column: nameOrig")

    customers = df["nameOrig"].dropna().astype(str)
    unique_ids = customers.unique().tolist()

    start = (page - 1) * limit
    end = start + limit
    page_ids = unique_ids[start:end]

    return [CustomerOut(id=str(cid)) for cid in page_ids]


def customer_profile(customer_id: str) -> CustomerProfileOut:
    df = get_dataset()
    df = _exclude_deleted(df)

    required = {"amount", "nameOrig", "nameDest"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

    as_origin = df[df["nameOrig"] == customer_id]
    as_dest = df[df["nameDest"] == customer_id]

    if as_origin.empty and as_dest.empty:
        raise KeyError("Customer not found")

    total_sent = float(as_origin["amount"].sum())
    total_received = float(as_dest["amount"].sum())

    return CustomerProfileOut(
        id=customer_id,
        total_sent=total_sent,
        total_received=total_received,
        transaction_count_as_origin=int(as_origin.shape[0]),
        transaction_count_as_destination=int(as_dest.shape[0]),
    )


def top_customers(n: int) -> TopCustomersOut:
    df = get_dataset()
    df = _exclude_deleted(df)

    if "nameOrig" not in df.columns:
        raise RuntimeError("Dataset missing required column: nameOrig")

    counts = df["nameOrig"].dropna().astype(str).value_counts()
    top = counts.head(n)

    customers = [CustomerOut(id=str(cid), transaction_count=int(cnt)) for cid, cnt in top.items()]
    return TopCustomersOut(n=n, customers=customers)
