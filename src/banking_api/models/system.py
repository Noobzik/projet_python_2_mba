"""System-related data models.

This module defines Pydantic models for system health and metadata.
"""

from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """System health check response.

    Parameters
    ----------
    status : str
        System status (ok, degraded, error).
    uptime : str
        System uptime duration.
    dataset_loaded : bool
        Whether the dataset is loaded.
    dataset_size : int
        Number of transactions in the dataset.
    """

    status: str
    uptime: str
    dataset_loaded: bool
    dataset_size: int = Field(..., ge=0)


class SystemMetadata(BaseModel):
    """System metadata information.

    Parameters
    ----------
    version : str
        API version.
    last_update : str
        Last update timestamp (ISO 8601 format).
    dataset_source : str
        Source of the dataset.
    endpoints_count : int
        Number of available endpoints.
    """

    version: str
    last_update: str
    dataset_source: str
    endpoints_count: int = Field(..., ge=0)
