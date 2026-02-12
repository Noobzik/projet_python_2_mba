"""
Transactions service for Banking Transactions API.

This module provides business logic for transaction operations including
filtering, searching, and pagination.
"""

from typing import List, Dict, Any, Optional
from app.utils.loader import load_transactions
from app.models.schemas import (
    TransactionResponse,
    PaginatedTransactionsResponse,
    TransactionSearchRequest,
)

_TRANSACTIONS: List[Dict[str, Any]] | None = None


def _get_data() -> List[Dict[str, Any]]:
    """
    Get cached transaction data.

    Returns
    -------
    List[Dict[str, Any]]
        List of transaction dictionaries
    """
    global _TRANSACTIONS
    if _TRANSACTIONS is None:
        _TRANSACTIONS = load_transactions()
        # Ajoute un ID si absent
        for i, tx in enumerate(_TRANSACTIONS):
            if "id" not in tx or not tx["id"]:
                tx["id"] = f"tx_{i:07d}"
    return _TRANSACTIONS


def get_transactions(
    page: int,
    limit: int,
    tx_type: Optional[str],
    is_fraud: Optional[int],
    min_amount: Optional[float],
    max_amount: Optional[float],
) -> PaginatedTransactionsResponse:
    """
    Get paginated list of transactions with optional filters.

    Parameters
    ----------
    page : int
        Page number (1-indexed)
    limit : int
        Items per page
    tx_type : Optional[str]
        Filter by transaction type
    is_fraud : Optional[int]
        Filter by fraud status (0 or 1)
    min_amount : Optional[float]
        Minimum amount filter
    max_amount : Optional[float]
        Maximum amount filter

    Returns
    -------
    PaginatedTransactionsResponse
        Paginated response with transactions
    """
    results = _get_data().copy()

    # Apply filters
    if tx_type:
        results = [t for t in results if t.get("type") == tx_type]

    if is_fraud is not None:
        results = [t for t in results if int(t.get("isFraud", 0)) == is_fraud]

    if min_amount is not None:
        results = [t for t in results if float(t.get("amount", 0)) >= min_amount]

    if max_amount is not None:
        results = [t for t in results if float(t.get("amount", 0)) <= max_amount]

    total = len(results)

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    page_results = results[start:end]

    # Convert to Pydantic models
    transactions = [
        TransactionResponse(**tx) for tx in page_results
    ]

    return PaginatedTransactionsResponse(
        page=page,
        limit=limit,
        total=total,
        transactions=transactions
    )


def get_transaction_by_id(transaction_id: str) -> Optional[Dict[str, Any]]:
    """
    Get transaction details by ID.

    Parameters
    ----------
    transaction_id : str
        Transaction ID

    Returns
    -------
    Optional[Dict[str, Any]]
        Transaction data or None if not found
    """
    for tx in _get_data():
        if tx.get("id") == transaction_id:
            return tx
    return None


def search_transactions(criteria: Dict[str, Any]) -> List[TransactionResponse]:
    """
    Search transactions with multiple criteria.

    Parameters
    ----------
    criteria : Dict[str, Any]
        Search criteria

    Returns
    -------
    List[TransactionResponse]
        Matching transactions
    """
    results = _get_data().copy()

    if criteria.get("type"):
        results = [t for t in results if t.get("type") == criteria["type"]]

    if criteria.get("isFraud") is not None:
        results = [t for t in results if int(t.get("isFraud", 0)) == criteria["isFraud"]]

    if criteria.get("amount_range"):
        min_a, max_a = criteria["amount_range"]
        results = [
            t for t in results
            if min_a <= float(t.get("amount", 0)) <= max_a
        ]

    if criteria.get("customer_id"):
        results = [
            t for t in results
            if t.get("nameOrig") == criteria["customer_id"]
            or t.get("nameDest") == criteria["customer_id"]
        ]

    # Limit to 1000 for performance
    results = results[:1000]

    # Convert to Pydantic models
    return [TransactionResponse(**tx) for tx in results]


def get_transaction_types() -> List[str]:
    """
    Get list of unique transaction types.

    Returns
    -------
    List[str]
        List of transaction types
    """
    types = {t.get("type") for t in _get_data() if t.get("type")}
    return sorted(list(types))


def get_recent_transactions(n: int) -> List[TransactionResponse]:
    """
    Get N most recent transactions.

    Parameters
    ----------
    n : int
        Number of transactions to return

    Returns
    -------
    List[TransactionResponse]
        Recent transactions
    """
    data = _get_data()
    recent = data[-n:] if len(data) >= n else data

    # Convert to Pydantic models
    return [TransactionResponse(**tx) for tx in recent]


def delete_transaction(transaction_id: str) -> bool:
    """
    Delete a transaction (test mode only).

    Parameters
    ----------
    transaction_id : str
        Transaction ID to delete

    Returns
    -------
    bool
        True if deleted, False if not found
    """
    global _TRANSACTIONS
    data = _get_data()
    initial_len = len(data)
    _TRANSACTIONS = [t for t in data if t.get("id") != transaction_id]
    return len(_TRANSACTIONS) < initial_len


def get_transactions_by_customer(customer_id: str) -> List[TransactionResponse]:
    """
    Get transactions where customer is the origin.

    Parameters
    ----------
    customer_id : str
        Customer ID

    Returns
    -------
    List[TransactionResponse]
        Transactions originated by customer
    """
    results = [t for t in _get_data() if t.get("nameOrig") == customer_id]
    return [TransactionResponse(**tx) for tx in results]


def get_transactions_to_customer(customer_id: str) -> List[TransactionResponse]:
    """
    Get transactions where customer is the destination.

    Parameters
    ----------
    customer_id : str
        Customer ID

    Returns
    -------
    List[TransactionResponse]
        Transactions received by customer
    """
    results = [t for t in _get_data() if t.get("nameDest") == customer_id]
    return [TransactionResponse(**tx) for tx in results]