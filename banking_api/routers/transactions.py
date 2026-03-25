"""
Transactions Router.

Exposes endpoints 1–8 for consultation, filtering, search and deletion
of banking transactions.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from banking_api.models.schemas import (
    MessageResponse,
    PaginatedTransactions,
    SearchRequest,
    TransactionOut,
)
from banking_api.services import transactions_service as svc

router: APIRouter = APIRouter()


@router.get("", response_model=PaginatedTransactions, summary="List transactions")
def list_transactions(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=1000, description="Records per page"),
    type: Optional[str] = Query(default=None, description="Transaction type filter"),
    isFraud: Optional[int] = Query(default=None, ge=0, le=1, description="Fraud flag"),
    min_amount: Optional[float] = Query(default=None, ge=0),
    max_amount: Optional[float] = Query(default=None, ge=0),
) -> PaginatedTransactions:
    """Return a paginated list of transactions with optional filters.

    Parameters
    ----------
    page : int
        Page number (1-indexed, default 1).
    limit : int
        Records per page (default 10, max 1 000).
    type : str, optional
        Filter by transaction type (e.g. TRANSFER, CASH_OUT).
    isFraud : int, optional
        Filter by fraud flag (0 or 1).
    min_amount : float, optional
        Minimum transaction amount.
    max_amount : float, optional
        Maximum transaction amount.

    Returns
    -------
    PaginatedTransactions
        Page metadata and list of transactions.
    """
    return svc.list_transactions(
        page=page,
        limit=limit,
        type_filter=type,
        is_fraud=isFraud,
        min_amount=min_amount,
        max_amount=max_amount,
    )


@router.get("/types", response_model=list[str], summary="List transaction types")
def get_types() -> list[str]:
    """Return all unique transaction types present in the dataset.

    Returns
    -------
    list[str]
        Sorted list of unique type values.
    """
    return svc.get_transaction_types()


@router.get(
    "/recent",
    response_model=list[TransactionOut],
    summary="Recent transactions",
)
def get_recent(
    n: int = Query(default=10, ge=1, le=1000, description="Number of records"),
) -> list[TransactionOut]:
    """Return the *n* most recent transactions.

    Parameters
    ----------
    n : int
        Number of transactions to return (default 10).

    Returns
    -------
    list[TransactionOut]
        Latest transactions.
    """
    return svc.get_recent_transactions(n=n)


@router.get(
    "/by-customer/{customer_id}",
    response_model=list[TransactionOut],
    summary="Transactions by originating customer",
)
def get_by_customer(customer_id: str) -> list[TransactionOut]:
    """Return all transactions sent by a given customer.

    Parameters
    ----------
    customer_id : str
        Customer identifier (``nameOrig`` value).

    Returns
    -------
    list[TransactionOut]
        Transactions where ``nameOrig`` matches *customer_id*.
    """
    return svc.get_transactions_by_customer(customer_id)


@router.get(
    "/to-customer/{customer_id}",
    response_model=list[TransactionOut],
    summary="Transactions received by customer",
)
def get_to_customer(customer_id: str) -> list[TransactionOut]:
    """Return all transactions received by a given customer.

    Parameters
    ----------
    customer_id : str
        Customer identifier (``nameDest`` value).

    Returns
    -------
    list[TransactionOut]
        Transactions where ``nameDest`` matches *customer_id*.
    """
    return svc.get_transactions_to_customer(customer_id)


@router.get(
    "/{transaction_id}",
    response_model=TransactionOut,
    summary="Get transaction by ID",
)
def get_transaction(transaction_id: str) -> TransactionOut:
    """Return a single transaction by its unique identifier.

    Parameters
    ----------
    transaction_id : str
        Unique identifier of the transaction (e.g. ``tx_0000001``).

    Returns
    -------
    TransactionOut
        Transaction detail.

    Raises
    ------
    HTTPException
        404 if the transaction does not exist.
    """
    result: Optional[TransactionOut] = svc.get_transaction_by_id(transaction_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result


@router.post(
    "/search",
    response_model=list[TransactionOut],
    summary="Multi-criteria search",
)
def search_transactions(request: SearchRequest) -> list[TransactionOut]:
    """Search transactions using multiple optional criteria.

    Parameters
    ----------
    request : SearchRequest
        JSON body with optional ``type``, ``isFraud``, ``amount_range``,
        ``nameOrig`` and ``nameDest`` filters.

    Returns
    -------
    list[TransactionOut]
        Matching transactions (max 1 000 results).
    """
    return svc.search_transactions(request)


@router.delete(
    "/{transaction_id}",
    response_model=MessageResponse,
    summary="Delete transaction (test mode)",
)
def delete_transaction(transaction_id: str) -> MessageResponse:
    """Soft-delete a transaction (test mode only).

    Parameters
    ----------
    transaction_id : str
        Unique identifier of the transaction to delete.

    Returns
    -------
    MessageResponse
        Confirmation message.

    Raises
    ------
    HTTPException
        404 if the transaction does not exist.
    """
    deleted: bool = svc.delete_transaction(transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return MessageResponse(message=f"Transaction {transaction_id} deleted successfully")
