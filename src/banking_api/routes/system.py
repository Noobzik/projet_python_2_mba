"""System routes.

This module defines API endpoints for system health and metadata.
"""

from fastapi import APIRouter
from ..models.system import HealthCheck, SystemMetadata
from ..services.system_service import SystemService

router = APIRouter(prefix="/api/system", tags=["system"])
service = SystemService()


@router.get("/health", response_model=HealthCheck)
def get_health() -> HealthCheck:
    """Check system health status.

    Returns
    -------
    HealthCheck
        System health information including status,
        uptime, and dataset status.
    """
    return service.get_health()


@router.get("/metadata", response_model=SystemMetadata)
def get_metadata() -> SystemMetadata:
    """Get system metadata.

    Returns
    -------
    SystemMetadata
        System metadata including version,
        last update, and endpoint count.
    """
    return service.get_metadata()
