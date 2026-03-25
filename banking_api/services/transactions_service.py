"""
Transactions Service.

Handles reading, pagination, filtering and multi-criteria search
of banking transactions.

Notes
-----
All public functions accept an optional ``df`` parameter so that unit
tests can inject a fixture DataFrame instead of relying on the singleton.
"""

from typing import Optional
import pandas as pd

from banking_api.models.schemas import (
    PaginatedTransactions,
    SearchRequest,
    TransactionOut,
)
from banking_api.services.data_loader import DataLoader


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_out(row: pd.Series) -> TransactionOut:  # type: ignore[type-arg]
    """Convert a DataFrame row to a ``TransactionOut`` instance.

    Parameters
    ----------
    row : pd.Series
        A single row from the transactions DataFrame.

    Returns
    -------
    TransactionOut
        Validated Pydantic model for the row.
    """
    return TransactionOut(
        id=str(row["id"]),
        step=int(row["step"]),
        type=str(row["type"]),
        amount=float(row["amount"]),
        nameOrig=str(row["nameOrig"]),
        oldbalanceOrg=float(row["oldbalanceOrg"]),
        newbalanceOrig=float(row["newbalanceOrig"]),
        nameDest=str(row["nameDest"]),
        oldbalanceDest=float(row["oldbalanceDest"]),
        newbalanceDest=float(row["newbalanceDest"]),
        isFraud=int(row["isFraud"]),
        isFlaggedFraud=int(row["isFlaggedFraud"]),
    )


def _get_df(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Return the provided DataFrame or fall back to the singleton.

    Parameters
    ----------
    df : pd.DataFrame or None
        Caller-supplied DataFrame (for tests) or ``None``.

    Returns
    -------
    pd.DataFrame
        The active dataset.
    """
    return df if df is not None else DataLoader.get_instance().df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def list_transactions(
    page: int = 1,
    limit: int = 10,
    type_filter: Optional[str] = None,
    is_fraud: Optional[int] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    df: Optional[pd.DataFrame] = None,
) -> PaginatedTransactions:
    """Return a paginated, optionally filtered list of transactions.

    Parameters
    ----------
    page : int
        Page number (1-indexed).
    limit : int
        Maximum number of records per page.
    type_filter : str, optional
        Keep only rows whose ``type`` column matches this value.
    is_fraud : int, optional
        Filter by fraud flag (0 or 1).
    min_amount : float, optional
        Minimum transaction amount (inclusive).
    max_amount : float, optional
        Maximum transaction amount (inclusive).
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    PaginatedTransactions
        Pydantic model containing page metadata and transaction list.
    """
    data: pd.DataFrame = _get_df(df).copy()

    if type_filter:
        data = data[data["type"] == type_filter]
    if is_fraud is not None:
        data = data[data["isFraud"] == is_fraud]
    if min_amount is not None:
        data = data[data["amount"] >= min_amount]
    if max_amount is not None:
        data = data[data["amount"] <= max_amount]

    total: int = len(data)
    start: int = (page - 1) * limit
    page_data: pd.DataFrame = data.iloc[start: start + limit]

    return PaginatedTransactions(
        page=page,
        limit=limit,
        total=total,
        transactions=[_row_to_out(r) for _, r in page_data.iterrows()],
    )


def get_transaction_by_id(
    transaction_id: str,
    df: Optional[pd.DataFrame] = None,
) -> Optional[TransactionOut]:
    """Return a single transaction by its ``id`` field.

    Parameters
    ----------
    transaction_id : str
        Unique transaction identifier (e.g. ``tx_0000001``).
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    TransactionOut or None
        The transaction model, or *None* if not found.
    """
    data: pd.DataFrame = _get_df(df)
    match: pd.DataFrame = data[data["id"] == transaction_id]
    if match.empty:
        return None
    return _row_to_out(match.iloc[0])


def search_transactions(
    request: SearchRequest,
    df: Optional[pd.DataFrame] = None,
) -> list[TransactionOut]:
    """Multi-criteria transaction search.

    Parameters
    ----------
    request : SearchRequest
        Pydantic model containing optional filter fields.
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[TransactionOut]
        Matching transactions (max 1 000 rows).
    """
    data: pd.DataFrame = _get_df(df).copy()

    if request.type:
        data = data[data["type"] == request.type]
    if request.isFraud is not None:
        data = data[data["isFraud"] == request.isFraud]
    if request.amount_range:
        lo, hi = request.amount_range
        data = data[(data["amount"] >= lo) & (data["amount"] <= hi)]
    if request.nameOrig:
        data = data[data["nameOrig"] == request.nameOrig]
    if request.nameDest:
        data = data[data["nameDest"] == request.nameDest]

    return [_row_to_out(r) for _, r in data.head(1000).iterrows()]


def get_transaction_types(df: Optional[pd.DataFrame] = None) -> list[str]:
    """Return the list of unique transaction types.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[str]
        Sorted unique values of the ``type`` column.
    """
    return sorted(_get_df(df)["type"].unique().tolist())


def get_recent_transactions(
    n: int = 10,
    df: Optional[pd.DataFrame] = None,
) -> list[TransactionOut]:
    """Return the *n* most recent transactions (last rows of dataset).

    Parameters
    ----------
    n : int
        Number of transactions to return (default 10).
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[TransactionOut]
        The last *n* rows of the dataset.
    """
    data: pd.DataFrame = _get_df(df).tail(n)
    return [_row_to_out(r) for _, r in data.iterrows()]


def delete_transaction(
    transaction_id: str,
) -> bool:
    """Soft-delete a transaction (test mode only).

    Parameters
    ----------
    transaction_id : str
        Unique transaction identifier.

    Returns
    -------
    bool
        *True* if deleted, *False* if not found.
    """
    return DataLoader.get_instance().soft_delete(transaction_id)


def get_transactions_by_customer(
    customer_id: str,
    df: Optional[pd.DataFrame] = None,
) -> list[TransactionOut]:
    """Return all transactions originating from a customer.

    Parameters
    ----------
    customer_id : str
        ``nameOrig`` value to filter on.
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[TransactionOut]
        Matching transactions.
    """
    data: pd.DataFrame = _get_df(df)
    match: pd.DataFrame = data[data["nameOrig"] == customer_id]
    return [_row_to_out(r) for _, r in match.iterrows()]


def get_transactions_to_customer(
    customer_id: str,
    df: Optional[pd.DataFrame] = None,
) -> list[TransactionOut]:
    """Return all transactions received by a customer.

    Parameters
    ----------
    customer_id : str
        ``nameDest`` value to filter on.
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[TransactionOut]
        Matching transactions.
    """
    data: pd.DataFrame = _get_df(df)
    match: pd.DataFrame = data[data["nameDest"] == customer_id]
    return [_row_to_out(r) for _, r in match.iterrows()]
