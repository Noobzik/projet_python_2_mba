"""
System service for Banking Transactions API.

This module provides system health checks and metadata information.
"""

from datetime import datetime, timezone
import time
from typing import Dict, Any, List
from app.utils.loader import load_transactions
from app.models.schemas import HealthResponse, MetadataResponse


# Store start time
_start_time = time.time()
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


def get_health() -> HealthResponse:
    """
    Check system health status.

    Returns
    -------
    HealthResponse
        System health information
    """
    # Calculate uptime
    uptime_seconds = int(time.time() - _start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60

    uptime_str = f"{hours}h {minutes}min"

    # Check if dataset is loaded
    try:
        data = _get_data()
        dataset_loaded = len(data) > 0
    except Exception:
        dataset_loaded = False

    status = "ok" if dataset_loaded else "degraded"

    return HealthResponse(
        status=status,
        uptime=uptime_str,
        dataset_loaded=dataset_loaded
    )


def get_metadata() -> MetadataResponse:
    """
    Get system metadata information.

    Returns
    -------
    MetadataResponse
        API version and last update timestamp
    """
    return MetadataResponse(
        version="1.0.0",
        last_update=datetime.now(timezone.utc).isoformat(),
    )