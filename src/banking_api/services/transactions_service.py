from __future__ import annotations

from typing import Optional

import pandas as pd

from banking_api.models.transaction import TransactionListOut, TransactionOut
from banking_api.services.dataset_loader import get_dataset
from banking_api.models.search import TransactionSearchIn
_DELETED_IDS: set[str] = set()


def _exclude_deleted(df: pd.DataFrame) -> pd.DataFrame:
    if not _DELETED_IDS:
        return df
    # Our tx id is based on row index: tx_<index>
    mask = [f"tx_{int(i):07d}" not in _DELETED_IDS for i in df.index]
    return df[mask]


def _apply_filters(
    df: pd.DataFrame,
    tx_type: Optional[str],
    is_fraud: Optional[bool],
    min_amount: Optional[float],
    max_amount: Optional[float],
) -> pd.DataFrame:
    if tx_type:
        df = df[df["type"] == tx_type]

    if is_fraud is not None and "isFraud" in df.columns:
        # dataset may store 0/1
        df = df[df["isFraud"].astype(int) == int(is_fraud)]

    if min_amount is not None:
        df = df[df["amount"] >= float(min_amount)]

    if max_amount is not None:
        df = df[df["amount"] <= float(max_amount)]

    return df


def list_transactions(
    page: int,
    limit: int,
    tx_type: Optional[str] = None,
    is_fraud: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> TransactionListOut:
    """
    List transactions with pagination and filters.
    """
    if min_amount is not None and max_amount is not None and float(min_amount) > float(max_amount):
        raise ValueError("min_amount cannot be greater than max_amount")

    df = get_dataset()
    df = _exclude_deleted(df)

    required = {"type", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    filtered = _apply_filters(df, tx_type, is_fraud, min_amount, max_amount)

    # Pagination
    offset = (page - 1) * limit
    page_df = filtered.iloc[offset : offset + limit]

    # Convert to API model with generated IDs based on original row index
    transactions: list[TransactionOut] = []
    for row_index, row in page_df.iterrows():
        transactions.append(TransactionOut.from_row(int(row_index), row.to_dict()))

    return TransactionListOut(page=page, transactions=transactions)


def get_transaction_by_id(tx_id: str) -> TransactionOut:
    """
    Get a transaction by its generated id (tx_<row_index>).
    """
    if not tx_id.startswith("tx_"):
        raise KeyError("Invalid transaction id format")

    raw = tx_id.replace("tx_", "")
    if not raw.isdigit():
        raise KeyError("Invalid transaction id format")

    row_index = int(raw)
    df = get_dataset()

    if row_index < 0 or row_index >= df.shape[0]:
        raise KeyError("Transaction not found")

    row = df.iloc[row_index].to_dict()
    return TransactionOut.from_row(row_index=row_index, row=row)


def get_transaction_types() -> list[str]:
    """
    Return available transaction types (unique values of column 'type').
    """
    df = get_dataset()
    if "type" not in df.columns:
        raise RuntimeError("Dataset missing required column: type")

    # pandas stubs often return Any; enforce list[str] explicitly
    values = df["type"].dropna().astype(str).unique()
    result = sorted(str(v) for v in values)
    return result


def get_recent_transactions(n: int = 10) -> list[TransactionOut]:
    """
    Return the N most recent transactions.

    Convention: 'recent' is based on the dataset order (last rows).
    """
    if n <= 0:
        return []

    df = get_dataset()
    df = _exclude_deleted(df)
    required = {"type", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    # Take last n rows, preserve dataset order (from oldest to newest within the slice)
    tail_df = df.tail(n)

    transactions: list[TransactionOut] = []
    for row_index, row in tail_df.iterrows():
        transactions.append(TransactionOut.from_row(int(row_index), row.to_dict()))
    return transactions


def delete_transaction_fake(tx_id: str) -> None:
    """
    Fake-delete a transaction (in-memory only).
    """
    # validate id format and existence
    _ = get_transaction_by_id(tx_id)
    _DELETED_IDS.add(tx_id)


def reset_deleted_ids() -> None:
    _DELETED_IDS.clear()


def search_transactions(criteria: TransactionSearchIn) -> list[TransactionOut]:
    """
    Search transactions using criteria (AND logic).

    Returns a list (not paginated) to match typical search behavior.
    """
    if (
        criteria.min_amount is not None
        and criteria.max_amount is not None
        and float(criteria.min_amount) > float(criteria.max_amount)
    ):
        raise ValueError("min_amount cannot be greater than max_amount")

    df = get_dataset()
    df = _exclude_deleted(df)

    required = {"type", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    filtered = _apply_filters(
        df,
        tx_type=criteria.type,
        is_fraud=criteria.isFraud,
        min_amount=criteria.min_amount,
        max_amount=criteria.max_amount,
    )

    if criteria.nameOrig is not None and "nameOrig" in filtered.columns:
        filtered = filtered[filtered["nameOrig"] == criteria.nameOrig]

    if criteria.nameDest is not None and "nameDest" in filtered.columns:
        filtered = filtered[filtered["nameDest"] == criteria.nameDest]

    results: list[TransactionOut] = []
    for row_index, row in filtered.iterrows():
        results.append(TransactionOut.from_row(int(row_index), row.to_dict()))
    return results


def get_transactions_by_customer(customer_id: str) -> list[TransactionOut]:
    df = get_dataset()
    df = _exclude_deleted(df)

    required = {"type", "amount", "nameOrig"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    filtered = df[df["nameOrig"] == customer_id]

    results: list[TransactionOut] = []
    for row_index, row in filtered.iterrows():
        results.append(TransactionOut.from_row(int(row_index), row.to_dict()))
    return results


def get_transactions_to_customer(customer_id: str) -> list[TransactionOut]:
    df = get_dataset()
    df = _exclude_deleted(df)

    required = {"type", "amount", "nameDest"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {sorted(missing)}")

    filtered = df[df["nameDest"] == customer_id]

    results: list[TransactionOut] = []
    for row_index, row in filtered.iterrows():
        results.append(TransactionOut.from_row(int(row_index), row.to_dict()))
    return results
