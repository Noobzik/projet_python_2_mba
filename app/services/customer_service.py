"""
Customer service for Banking Transactions API.

This module provides customer profile aggregation and analysis.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from statistics import mean
from app.utils.loader import load_transactions
from app.models.schemas import (
    Customer,
    PaginatedCustomersResponse,
    TopCustomer,
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
    return _TRANSACTIONS


def get_customers(page: int, limit: int) -> PaginatedCustomersResponse:
    """
    Get paginated list of unique customer IDs.

    Parameters
    ----------
    page : int
        Page number
    limit : int
        Items per page

    Returns
    -------
    PaginatedCustomersResponse
        Paginated customer list
    """
    data = _get_data()
    
    # Get unique customer IDs from nameOrig
    unique_customers = sorted({t.get("nameOrig") for t in data if t.get("nameOrig")})
    total = len(unique_customers)

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    customers_page = unique_customers[start:end]

    return PaginatedCustomersResponse(
        page=page,
        limit=limit,
        total=total,
        customers=customers_page
    )


def get_customer_profile(customer_id: str) -> Optional[Customer]:
    """
    Get comprehensive customer profile.

    Parameters
    ----------
    customer_id : str
        Customer ID

    Returns
    -------
    Optional[Customer]
        Customer profile or None if not found
    """
    data = _get_data()
    
    # Get all transactions for this customer (as origin)
    customer_txs = [t for t in data if t.get("nameOrig") == customer_id]

    if not customer_txs:
        return None

    transactions_count = len(customer_txs)
    amounts = [float(t.get("amount", 0)) for t in customer_txs]
    avg_amount = mean(amounts) if amounts else 0.0
    total_amount = sum(amounts)
    fraudulent = any(int(t.get("isFraud", 0)) == 1 for t in customer_txs)

    return Customer(
        id=customer_id,
        transactions_count=transactions_count,
        avg_amount=round(avg_amount, 2),
        total_amount=round(total_amount, 2),
        fraudulent=fraudulent,
    )


def get_top_customers(n: int) -> List[TopCustomer]:
    """
    Get top N customers by transaction volume.

    Parameters
    ----------
    n : int
        Number of top customers to return

    Returns
    -------
    List[TopCustomer]
        Top customers ranked by total amount
    """
    data = _get_data()
    
    # Aggregate by customer
    customer_stats = defaultdict(lambda: {"total_amount": 0.0, "count": 0})

    for t in data:
        customer_id = t.get("nameOrig")
        if customer_id:
            customer_stats[customer_id]["total_amount"] += float(t.get("amount", 0))
            customer_stats[customer_id]["count"] += 1

    # Sort by total amount descending
    ranked = sorted(
        customer_stats.items(),
        key=lambda x: x[1]["total_amount"],
        reverse=True
    )[:n]

    # Convert to TopCustomer objects
    top_customers = [
        TopCustomer(
            customer_id=customer_id,
            total_amount=round(stats["total_amount"], 2),
            transaction_count=stats["count"],
        )
        for customer_id, stats in ranked
    ]

    return top_customers