"""
System Service.

Provides diagnostic information and service metadata.
"""

import time

from banking_api.models.schemas import HealthResponse, MetadataResponse
from banking_api.services.data_loader import DataLoader

_START_TIME: float = time.time()
_LAST_UPDATE: str = "2025-12-20T22:00:00Z"
_VERSION: str = "1.0.0"


def get_health() -> HealthResponse:
    """Return the current health status of the API.

    Returns
    -------
    HealthResponse
        Status string, human-readable uptime and dataset load flag.
    """
    elapsed: float = time.time() - _START_TIME
    hours: int = int(elapsed // 3600)
    minutes: int = int((elapsed % 3600) // 60)
    uptime: str = f"{hours}h {minutes:02d}min"

    loader: DataLoader = DataLoader.get_instance()

    return HealthResponse(
        status="ok",
        uptime=uptime,
        dataset_loaded=loader.is_loaded,
    )


def get_metadata() -> MetadataResponse:
    """Return service version and last-update timestamp.

    Returns
    -------
    MetadataResponse
        Version string and ISO-8601 last-update date.
    """
    return MetadataResponse(
        version=_VERSION,
        last_update=_LAST_UPDATE,
    )
