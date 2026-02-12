"""
Transactions router for Banking Transactions API.

This module defines the API endpoints for transaction operations.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.models.schemas import (
    TransactionResponse,
    PaginatedTransactionsResponse,
    TransactionSearchRequest,
)
from app.services.transactions_service import (
    get_transactions,
    get_transaction_by_id,
    search_transactions,
    get_transaction_types,
    get_recent_transactions,
    delete_transaction,
    get_transactions_by_customer,
    get_transactions_to_customer,
)

router = APIRouter(tags=["Transactions"])


# 1️⃣ GET /api/transactions
@router.get("/transactions", response_model=PaginatedTransactionsResponse)
def list_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by transaction type"),
    isFraud: Optional[int] = Query(None, ge=0, le=1, description="Filter by fraud status"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount"),
) -> PaginatedTransactionsResponse:
    """
    Get paginated list of transactions with optional filters.

    Parameters
    ----------
    page : int
        Page number (starting from 1)
    limit : int
        Number of items per page (max 1000)
    type : Optional[str]
        Filter by transaction type
    isFraud : Optional[int]
        Filter by fraud status (0 or 1)
    min_amount : Optional[float]
        Minimum transaction amount
    max_amount : Optional[float]
        Maximum transaction amount

    Returns
    -------
    PaginatedTransactionsResponse
        Paginated list of transactions
    """
    return get_transactions(page, limit, type, isFraud, min_amount, max_amount)


# 2️⃣ GET /api/transactions/{transaction_id}
@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str) -> TransactionResponse:
    """
    Get transaction details by ID.

    Parameters
    ----------
    transaction_id : str
        Transaction ID (format: tx_XXXXX)

    Returns
    -------
    TransactionResponse
        Transaction details

    Raises
    ------
    HTTPException
        404 if transaction not found
    """
    tx = get_transaction_by_id(transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse(**tx)


# 3️⃣ POST /api/transactions/search
@router.post("/transactions/search", response_model=List[TransactionResponse])
def search(request: TransactionSearchRequest) -> List[TransactionResponse]:
    """
    Search transactions with multiple criteria.

    Parameters
    ----------
    request : TransactionSearchRequest
        Search criteria (type, isFraud, amount_range, customer_id)

    Returns
    -------
    List[TransactionResponse]
        List of matching transactions (max 1000)
    """
    return search_transactions(request.dict(exclude_none=True))


# 4️⃣ GET /api/transactions/types
@router.get("/transactions/types", response_model=List[str])
def get_types() -> List[str]:
    """
    Get list of available transaction types.

    Returns
    -------
    List[str]
        Unique transaction types
    """
    return get_transaction_types()


# 5️⃣ GET /api/transactions/recent
@router.get("/transactions/recent", response_model=List[TransactionResponse])
def get_recent(n: int = Query(10, ge=1, le=100, description="Number of recent transactions")) -> List[TransactionResponse]:
    """
    Get N most recent transactions.

    Parameters
    ----------
    n : int
        Number of transactions to return (default: 10, max: 100)

    Returns
    -------
    List[TransactionResponse]
        Recent transactions sorted by time step
    """
    return get_recent_transactions(n)


# 6️⃣ DELETE /api/transactions/{transaction_id}
@router.delete("/transactions/{transaction_id}")
def delete(transaction_id: str) -> dict:
    """
    Delete a transaction (test mode only).

    Parameters
    ----------
    transaction_id : str
        Transaction ID to delete

    Returns
    -------
    dict
        Success message

    Raises
    ------
    HTTPException
        404 if transaction not found
    """
    deleted = delete_transaction(transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": f"Transaction {transaction_id} deleted successfully"}


# 7️⃣ GET /api/transactions/by-customer/{customer_id}
@router.get("/transactions/by-customer/{customer_id}", response_model=List[TransactionResponse])
def by_customer(customer_id: str) -> List[TransactionResponse]:
    """
    Get transactions where customer is the origin.

    Parameters
    ----------
    customer_id : str
        Customer ID

    Returns
    -------
    List[TransactionResponse]
        Transactions originated by the customer
    """
    return get_transactions_by_customer(customer_id)


# 8️⃣ GET /api/transactions/to-customer/{customer_id}
@router.get("/transactions/to-customer/{customer_id}", response_model=List[TransactionResponse])
def to_customer(customer_id: str) -> List[TransactionResponse]:
    """
    Get transactions where customer is the destination.

    Parameters
    ----------
    customer_id : str
        Customer ID

    Returns
    -------
    List[TransactionResponse]
        Transactions received by the customer
    """
    return get_transactions_to_customer(customer_id)