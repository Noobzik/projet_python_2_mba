"""Service système pour les contrôles de santé et les métadonnées.

Ce module gère les opérations au niveau système incluant :
contrôle de santé, informations de métadonnées et diagnostics du service.
"""
import time
from datetime import timedelta
from typing import Dict, Union
from banking_api.utils.data_loader import DataLoader
from banking_api.models.schemas import HealthResponse, MetadataResponse
from banking_api.config import API_VERSION, LAST_UPDATE


class SystemService:
    """Classe de service pour les opérations système.

    Attributes
    ----------
    data_loader : DataLoader
        Instance du chargeur de données
    start_time : float
        Horodatage de démarrage du service

    Notes
    -----
    Ce service fournit des informations critiques pour le monitoring
    et la supervision de l'état de l'API en production.
    """

    def __init__(self) -> None:
        """Initialiser le service système.

        Notes
        -----
        Enregistre le temps de démarrage pour le calcul de l'uptime.
        """
        self.data_loader = DataLoader()
        self.start_time = time.time()

    def _format_uptime(self, seconds: float) -> str:
        """Formater le temps de fonctionnement en format lisible.

        Parameters
        ----------
        seconds : float
            Temps de fonctionnement en secondes

        Returns
        -------
        str
            Chaîne formatée du temps de fonctionnement (ex: '2d 5h 30m 15s')

        Examples
        --------
        >>> service = SystemService()
        >>> formatted = service._format_uptime(90061)
        >>> print(formatted)
        '1d 1h 1m 1s'

        Notes
        -----
        Méthode interne utilisée pour améliorer la lisibilité
        du temps de fonctionnement dans les réponses d'état de santé.
        """
        delta = timedelta(seconds=int(seconds))
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)

    def get_health(self) -> HealthResponse:
        """Récupérer l'état de santé du système.

        Returns
        -------
        HealthResponse
            Objet contenant :
            - status : État du service ('ok' ou 'degraded')
            - uptime : Temps de fonctionnement formaté
            - dataset_loaded : Statut de chargement des données
            - total_records : Nombre total d'enregistrements

        Examples
        --------
        >>> service = SystemService()
        >>> health = service.get_health()
        >>> print(health.status)
        'ok'
        >>> print(health.total_records)
        6362620

        Notes
        -----
        Le statut est 'ok' si le dataset est chargé, 'degraded' sinon.
        Cette route est utilisée pour les health checks Kubernetes/Docker.
        """
        uptime_seconds = time.time() - self.start_time
        uptime_str = self._format_uptime(uptime_seconds)
        dataset_loaded = self.data_loader.is_loaded
        total_records = self.data_loader.record_count

        status = "ok" if dataset_loaded else "degraded"

        return HealthResponse(
            status=status,
            uptime=uptime_str,
            dataset_loaded=dataset_loaded,
            total_records=total_records
        )

    def get_metadata(self) -> MetadataResponse:
        """Récupérer les informations de métadonnées système.

        Returns
        -------
        MetadataResponse
            Objet contenant :
            - version : Version de l'API
            - last_update : Date de dernière mise à jour
            - total_endpoints : Nombre total d'endpoints disponibles
            - dataset_info : Informations sur le dataset (nom, taille, etc.)

        Examples
        --------
        >>> service = SystemService()
        >>> metadata = service.get_metadata()
        >>> print(metadata.version)
        '1.0.0'
        >>> print(metadata.dataset_info['records'])
        6362620

        Notes
        -----
        Les informations de métadonnées sont utiles pour la documentation
        automatique et le monitoring des performances du système.
        La taille en MB est calculée en incluant l'utilisation mémoire profonde.
        """
        df = self.data_loader.get_data()

        dataset_info: Dict[str, Union[str, int]] = {
            "name": "transactions_data.csv",
            "records": len(df),
            "columns": len(df.columns),
            "size_mb": int(
                round(df.memory_usage(deep=True).sum() / (1024 * 1024))
            )
        }

        total_endpoints = 20

        return MetadataResponse(
            version=API_VERSION,
            last_update=LAST_UPDATE,
            total_endpoints=total_endpoints,
            dataset_info=dataset_info
        )