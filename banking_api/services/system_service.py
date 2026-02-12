"""
Service système pour la santé et les métadonnées de l'API.

Ce module fournit les fonctionnalités de diagnostic et d'information
sur l'état du service.
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from banking_api.models.schemas import SystemHealth, SystemMetadata
from banking_api.services.data_loader import data_loader


class SystemService:
    """
    Service système.

    Cette classe fournit les opérations de diagnostic et de métadonnées
    pour le monitoring de l'API.
    """

    def __init__(self) -> None:
        """Initialise le service système."""
        self.data_loader = data_loader
        self.start_time: datetime = datetime.now()
        self.version: str = "1.0.0"
        self.last_update: str = "2025-11-18T00:00:00Z"

    def get_health(self) -> SystemHealth:
        """
        Vérifie l'état de santé de l'API.

        Returns
        -------
        SystemHealth
            État de santé du système
        """
        # Calcul de l'uptime
        uptime_delta: timedelta = datetime.now() - self.start_time
        hours: int = int(uptime_delta.total_seconds() // 3600)
        minutes: int = int((uptime_delta.total_seconds() % 3600) // 60)
        uptime_str: str = f"{hours}h {minutes}min"

        # Vérification du chargement des données
        dataset_loaded: bool = self.data_loader.is_loaded()

        # Détermination du statut
        status: str = "ok" if dataset_loaded else "degraded"

        return SystemHealth(
            status=status,
            uptime=uptime_str,
            dataset_loaded=dataset_loaded,
            timestamp=datetime.now().isoformat(),
        )

    def get_metadata(self) -> SystemMetadata:
        """
        Retourne les métadonnées du système.

        Returns
        -------
        SystemMetadata
            Métadonnées de l'API
        """
        total_transactions: int = 0
        if self.data_loader.is_loaded():
            df = self.data_loader.get_transactions()
            total_transactions = len(df)

        return SystemMetadata(
            version=self.version,
            last_update=self.last_update,
            total_transactions=total_transactions,
            data_source="Kaggle - Transactions Fraud Datasets",
        )

    def get_system_info(self) -> Dict[str, Any]:
        """
        Retourne des informations détaillées sur le système.

        Returns
        -------
        Dict[str, Any]
            Informations système détaillées
        """
        health: SystemHealth = self.get_health()
        metadata: SystemMetadata = self.get_metadata()

        system_info: Dict[str, Any] = {
            "health": {
                "status": health.status,
                "uptime": health.uptime,
                "dataset_loaded": health.dataset_loaded,
                "timestamp": health.timestamp,
            },
            "metadata": {
                "version": metadata.version,
                "last_update": metadata.last_update,
                "total_transactions": metadata.total_transactions,
                "data_source": metadata.data_source,
            },
            "environment": {
                "python_version": "3.12+",
                "framework": "FastAPI",
                "data_format": "CSV/JSON",
            },
        }

        return system_info

    def check_dataset_integrity(self) -> Dict[str, Any]:
        """
        Vérifie l'intégrité du dataset.

        Returns
        -------
        Dict[str, Any]
            Rapport d'intégrité des données
        """
        if not self.data_loader.is_loaded():
            return {"status": "error", "message": "Dataset not loaded"}

        df = self.data_loader.get_transactions()

        integrity_report: Dict[str, Any] = {
            "status": "ok",
            "total_records": len(df),
            "columns": df.columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
        }

        return integrity_report


# Instance globale du service
system_service: SystemService = SystemService()
