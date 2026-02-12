"""
System router for Banking Transactions API.

This module defines the API endpoints for system administration and monitoring.
"""

from fastapi import APIRouter
from app.models.schemas import HealthResponse, MetadataResponse
from app.services.system_service import (
    get_health,
    get_metadata,
)

router = APIRouter(tags=["System"])


# 19️⃣ GET /api/system/health
@router.get("/system/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Check API health status.

    Returns
    -------
    HealthResponse
        System health information including:
        - status: Service status (ok/degraded)
        - uptime: Service uptime
        - dataset_loaded: Dataset load status
    """
    return get_health()


# 20️⃣ GET /api/system/metadata
@router.get("/system/metadata", response_model=MetadataResponse)
def metadata() -> MetadataResponse:
    """
    Get API metadata information.

    Returns
    -------
    MetadataResponse
        API metadata including:
        - version: API version
        - last_update: Last update timestamp
    """
    return get_metadata()
