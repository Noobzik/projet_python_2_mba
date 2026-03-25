"""
Banking Transactions API - Main Application Entry Point.

This module initialises and configures the FastAPI application,
registers all routers and exposes a ``run`` entry point for the
installed console-script.
"""

import time
import uvicorn
from fastapi import FastAPI

from banking_api.routers import (
    transactions,
    stats,
    fraud,
    customers,
    system,
)
from banking_api.services.data_loader import DataLoader

# ---------------------------------------------------------------------------
# Application startup timestamp (used by /api/system/health)
# ---------------------------------------------------------------------------
START_TIME: float = time.time()

app: FastAPI = FastAPI(
    title="Banking Transactions API",
    description=(
        "REST API exposing banking transaction data for the portfolio "
        "management application."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Lifespan: pre-load dataset once at startup
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def startup_event() -> None:
    """Load the CSV dataset into memory when the application starts."""
    DataLoader.get_instance()


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(
    transactions.router, prefix="/api/transactions", tags=["Transactions"]
)
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(fraud.router, prefix="/api/fraud", tags=["Fraud"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(system.router, prefix="/api/system", tags=["Administration"])


def run() -> None:
    """Console-script entry point."""
    uvicorn.run(
        "banking_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    run()
