"""Routes package initialization.

This module exports all API route routers.
"""

from banking_api.routes.customers import router as customers_router
from banking_api.routes.fraud import router as fraud_router
from banking_api.routes.stats import router as stats_router
from banking_api.routes.system import router as system_router
from banking_api.routes.transactions import router as transactions_router

__all__ = [
    "transactions_router",
    "stats_router",
    "fraud_router",
    "customers_router",
    "system_router",
]
