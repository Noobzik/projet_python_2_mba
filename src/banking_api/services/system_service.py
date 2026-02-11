"""System service layer.

This module provides business logic for system health and metadata.
"""

import time
from datetime import datetime, timezone
from ..models.system import HealthCheck, SystemMetadata
from ..utils.data_loader import DataLoader


class SystemService:
    """Service for system health and metadata operations.

    Attributes
    ----------
    start_time : float
        Service start timestamp.
    """

    def __init__(self) -> None:
        """Initialize the system service."""
        self.data_loader = DataLoader()
        self.start_time = time.time()

    def get_health(self) -> HealthCheck:
        """Get system health status.

        Returns
        -------
        HealthCheck
            Health check response with system status.
        """
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60

        dataset_loaded = self.data_loader.is_loaded()
        dataset_size = 0

        if dataset_loaded:
            dataset_size = len(self.data_loader.get_data())

        status = "ok" if dataset_loaded else "degraded"

        return HealthCheck(
            status=status,
            uptime=f"{hours}h {minutes}min",
            dataset_loaded=dataset_loaded,
            dataset_size=dataset_size
        )

    def get_metadata(self) -> SystemMetadata:
        """Get system metadata.

        Returns
        -------
        SystemMetadata
            System metadata including version and update info.
        """
        last_update = datetime.now(timezone.utc).isoformat()

        return SystemMetadata(
            version="1.0.0",
            last_update=last_update,
            dataset_source="Kaggle - Transactions Fraud Datasets",
            endpoints_count=20
        )
