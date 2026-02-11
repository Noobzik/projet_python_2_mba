"""Transaction routes.

This module defines API endpoints for transaction operations.
"""

from typing import Optional, List, Union
from fastapi import APIRouter, HTTPException, Query
from ..models.transaction import (
    Transaction,
    TransactionList,
    TransactionSearch
)
from ..services.transactions_service import TransactionsService

router = APIRouter(prefix="/api/transactions", tags=["transactions"])
service = TransactionsService()


@router.get("", response_model=TransactionList)
def get_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    use_chip: Optional[str] = Query(None, description="Transaction method filter"),
    isFraud: Optional[Union[int, bool, str]] = Query(
        None,
        description="Fraud filter (0/1, true/false, or yes/no)"
    ),
    min_amount: Optional[float] = Query(None, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, description="Maximum amount"),
    merchant_state: Optional[str] = Query(None, description="Merchant state filter")
) -> TransactionList:
    """Get paginated list of transactions.

    Parameters
    ----------
    page : int
        Page number (default: 1).
    limit : int
        Items per page (default: 50, max: 100).
    use_chip : Optional[str]
        Filter by transaction method (Swipe, Chip, Online).
    isFraud : Optional[Union[int, bool, str]]
        Filter by fraud status (0/1, true/false, or yes/no).
    min_amount : Optional[float]
        Minimum transaction amount.
    max_amount : Optional[float]
        Maximum transaction amount.
    merchant_state : Optional[str]
        Filter by merchant state.

    Returns
    -------
    TransactionList
        Paginated list of transactions.
    """
    # Convert isFraud to int if provided
    is_fraud_int = None
    if isFraud is not None:
        if isinstance(isFraud, bool):
            is_fraud_int = 1 if isFraud else 0
        elif isinstance(isFraud, str):
            is_fraud_int = 1 if isFraud.lower() in ('true', 'yes', '1') else 0
        else:
            is_fraud_int = int(isFraud)

    return service.get_transactions(
        page=page,
        limit=limit,
        use_chip_filter=use_chip,
        is_fraud=is_fraud_int,
        min_amount=min_amount,
        max_amount=max_amount,
        merchant_state=merchant_state
    )


@router.get("/types", response_model=List[str])
def get_transaction_types() -> List[str]:
    """Get list of available transaction types.

    Returns
    -------
    List[str]
        List of unique transaction types (Swipe, Chip, Online).
    """
    return service.get_transaction_methods()


@router.get("/recent", response_model=List[Transaction])
def get_recent_transactions(
    n: int = Query(10, ge=1, le=100, description="Number of recent transactions")
) -> List[Transaction]:
    """Get N most recent transactions.

    Parameters
    ----------
    n : int
        Number of recent transactions (default: 10, max: 100).

    Returns
    -------
    List[Transaction]
        List of recent transactions.
    """
    return service.get_recent_transactions(n)


@router.post("/search", response_model=TransactionList)
def search_transactions(
    criteria: TransactionSearch,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
) -> TransactionList:
    """Search transactions with multiple criteria.

    Parameters
    ----------
    criteria : TransactionSearch
        Search criteria (use_chip, isFraud, amount_range, etc.).
    page : int
        Page number.
    limit : int
        Items per page.

    Returns
    -------
    TransactionList
        Paginated list of matching transactions.
    """
    return service.search_transactions(criteria, page, limit)


@router.get("/by-customer/{customer_id}", response_model=TransactionList)
def get_transactions_by_customer(
    customer_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page")
) -> TransactionList:
    """Get paginated transactions by a customer.

    Parameters
    ----------
    customer_id : int
        Customer identifier.
    page : int
        Page number (default: 1).
    limit : int
        Items per page (default: 50, max: 100).

    Returns
    -------
    TransactionList
        Paginated list of transactions from this customer.
    """
    return service.get_transactions_by_client(customer_id, page, limit)


@router.get("/to-customer/{customer_id}", response_model=List[Transaction])
def get_transactions_to_customer(
    customer_id: int
) -> List[Transaction]:
    """Get transactions received by a customer.

    Note: Since the Kaggle credit card fraud dataset only contains
    customer-to-merchant transactions (not customer-to-customer transfers),
    this endpoint interprets customer_id as merchant_id and returns
    transactions where the merchant received payments.

    Parameters
    ----------
    customer_id : int
        Customer identifier (interpreted as merchant_id for this dataset).

    Returns
    -------
    List[Transaction]
        List of transactions received by the merchant.
    """
    # The Kaggle dataset doesn't have customer-to-customer transactions
    # So we interpret the customer_id as merchant_id to show received payments
    return service.get_transactions_to_merchant(customer_id)



@router.get("/{id}", response_model=Transaction)
def get_transaction_by_id(id: str) -> Transaction:
    """Get transaction details by ID.

    Parameters
    ----------
    id : str
        Transaction identifier.

    Returns
    -------
    Transaction
        Transaction details.

    Raises
    ------
    HTTPException
        404 if transaction not found.
    """
    transaction = service.get_transaction_by_id(id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.delete("/{id}")
def delete_transaction(id: str) -> dict:
    """Delete a transaction (test mode only).

    Parameters
    ----------
    id : str
        Transaction identifier.

    Returns
    -------
    dict
        Status message.

    Raises
    ------
    HTTPException
        404 if transaction not found.
    """
    if not service.delete_transaction(id):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"status": "deleted", "id": id}
