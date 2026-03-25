"""
Customer Service.

Aggregates transaction data by originating customer (``nameOrig``).
"""

from typing import Optional
import pandas as pd

from banking_api.models.schemas import (
    CustomerProfile,
    CustomerSummary,
    TopCustomer,
)
from banking_api.services.data_loader import DataLoader


def _get_df(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Return provided DataFrame or singleton dataset.

    Parameters
    ----------
    df : pd.DataFrame or None
        Caller-supplied DataFrame (tests) or ``None``.

    Returns
    -------
    pd.DataFrame
        Active dataset.
    """
    return df if df is not None else DataLoader.get_instance().df


def list_customers(
    page: int = 1,
    limit: int = 10,
    df: Optional[pd.DataFrame] = None,
) -> list[CustomerSummary]:
    """Return a paginated list of unique originating customers.

    Parameters
    ----------
    page : int
        Page number (1-indexed).
    limit : int
        Records per page.
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[CustomerSummary]
        Lightweight customer summaries.
    """
    data: pd.DataFrame = _get_df(df)
    grouped: pd.DataFrame = (
        data.groupby("nameOrig")
        .size()
        .reset_index(name="transactions_count")
    )

    start: int = (page - 1) * limit
    page_data: pd.DataFrame = grouped.iloc[start: start + limit]

    return [
        CustomerSummary(
            id=str(row["nameOrig"]),
            transactions_count=int(row["transactions_count"]),
        )
        for _, row in page_data.iterrows()
    ]


def get_customer_profile(
    customer_id: str,
    df: Optional[pd.DataFrame] = None,
) -> Optional[CustomerProfile]:
    """Build a synthetic profile for a single customer.

    Parameters
    ----------
    customer_id : str
        The ``nameOrig`` identifier of the customer.
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    CustomerProfile or None
        Aggregated profile, or *None* if the customer is not found.
    """
    data: pd.DataFrame = _get_df(df)
    customer_data: pd.DataFrame = data[data["nameOrig"] == customer_id]

    if customer_data.empty:
        return None

    return CustomerProfile(
        id=customer_id,
        transactions_count=len(customer_data),
        avg_amount=round(float(customer_data["amount"].mean()), 2),
        fraudulent=bool(customer_data["isFraud"].any()),
    )


def get_top_customers(
    n: int = 10,
    df: Optional[pd.DataFrame] = None,
) -> list[TopCustomer]:
    """Return the top *n* customers ranked by total transaction volume.

    Parameters
    ----------
    n : int
        Number of customers to return (default 10).
    df : pd.DataFrame, optional
        Injected DataFrame (tests only).

    Returns
    -------
    list[TopCustomer]
        Customers sorted by descending total volume.
    """
    data: pd.DataFrame = _get_df(df)
    grouped: pd.DataFrame = (
        data.groupby("nameOrig")
        .agg(total_volume=("amount", "sum"), transactions_count=("amount", "count"))
        .reset_index()
        .sort_values("total_volume", ascending=False)
        .head(n)
    )

    return [
        TopCustomer(
            id=str(row["nameOrig"]),
            total_volume=round(float(row["total_volume"]), 2),
            transactions_count=int(row["transactions_count"]),
        )
        for _, row in grouped.iterrows()
    ]
