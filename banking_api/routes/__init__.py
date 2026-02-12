"""Routes package."""

from banking_api.routes import (
    customers,
    fraud,
    statistics,
    system,
    transactions,
)

__all__ = [
    "transactions",
    "statistics",
    "fraud",
    "customers",
    "system",
]
