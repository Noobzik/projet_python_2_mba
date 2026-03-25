"""
System Router.

Exposes endpoints 19–20 for health-check and service metadata.
"""

from fastapi import APIRouter

from banking_api.models.schemas import HealthResponse, MetadataResponse
from banking_api.services import system_service as svc

router: APIRouter = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check() -> HealthResponse:
    """Return the current health status of the API.

    Returns
    -------
    HealthResponse
        Status, uptime and dataset load flag.
    """
    return svc.get_health()


@router.get("/metadata", response_model=MetadataResponse, summary="Service metadata")
def get_metadata() -> MetadataResponse:
    """Return version and last-update metadata.

    Returns
    -------
    MetadataResponse
        Service version and last update timestamp.
    """
    return svc.get_metadata()
