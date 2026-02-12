"""
Modèles Pydantic pour l'API Banking Transactions.

Ce module contient tous les modèles de données utilisés dans l'API,
incluant les transactions, statistiques, et réponses API.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Transaction(BaseModel):
    """
    Modèle représentant une transaction bancaire par carte.

    Attributes
    ----------
    id : int
        Identifiant unique de la transaction
    date : str
        Date et heure de la transaction
    client_id : int
        Identifiant du client
    card_id : int
        Identifiant de la carte
    amount : float
        Montant de la transaction
    use_chip : Optional[str]
        Utilisation de la puce (Chip Transaction, Swipe Transaction, Online Transaction)
    merchant_id : int
        Identifiant du marchand
    merchant_city : str
        Ville du marchand
    merchant_state : str
        État du marchand
    zip : Optional[float]
        Code postal
    mcc : int
        Merchant Category Code
    errors : Optional[str]
        Erreurs éventuelles
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identifiant unique de la transaction")
    date: str = Field(..., description="Date et heure de la transaction")
    client_id: int = Field(..., description="Identifiant du client")
    card_id: int = Field(..., description="Identifiant de la carte")
    amount: float = Field(
        ...,
        description="Montant de la transaction (peut être négatif pour les remboursements)",
    )
    use_chip: Optional[str] = Field(None, description="Type d'utilisation de la carte")
    merchant_id: int = Field(..., description="Identifiant du marchand")
    merchant_city: str = Field(..., description="Ville du marchand")
    merchant_state: str = Field(..., description="État du marchand")
    zip: Optional[float] = Field(None, description="Code postal")
    mcc: int = Field(..., description="Merchant Category Code")
    errors: Optional[str] = Field(None, description="Erreurs")


class TransactionResponse(BaseModel):
    """
    Réponse paginée pour les transactions.

    Attributes
    ----------
    page : int
        Numéro de page actuelle
    limit : int
        Nombre d'éléments par page
    total : int
        Nombre total de transactions
    transactions : List[Transaction]
        Liste des transactions
    """

    page: int = Field(..., description="Numéro de page")
    limit: int = Field(..., description="Nombre d'éléments par page")
    total: int = Field(..., description="Nombre total de transactions")
    transactions: List[Transaction] = Field(..., description="Liste des transactions")


class TransactionSearch(BaseModel):
    """
    Critères de recherche pour les transactions.

    Attributes
    ----------
    page : Optional[int]
        Numéro de page
    limit : Optional[int]
        Nombre d'éléments par page
    use_chip : Optional[str]
        Type d'utilisation de la carte
    isFraud : Optional[bool]
        Filtre sur les transactions frauduleuses
    amount_range : Optional[List[float]]
        Plage de montants [min, max]
    client_id : Optional[int]
        Identifiant du client
    card_id : Optional[int]
        Identifiant de la carte
    merchant_id : Optional[int]
        Identifiant du marchand
    merchant_state : Optional[str]
        État du marchand
    mcc : Optional[int]
        Merchant Category Code
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "page": 1,
                    "limit": 50,
                    "use_chip": "Chip Transaction",
                    "isFraud": True,
                    "amount_range": [100, 1000],
                }
            ]
        }
    }

    page: Optional[int] = Field(1, ge=1, description="Numéro de page")
    limit: Optional[int] = Field(
        50, ge=1, le=1000, description="Nombre d'éléments par page"
    )
    use_chip: Optional[str] = Field(None, description="Type d'utilisation de la carte")
    isFraud: Optional[bool] = Field(
        None, description="Filtre sur les transactions frauduleuses"
    )
    amount_range: Optional[List[float]] = Field(
        None, min_length=2, max_length=2, description="Plage de montants [min, max]"
    )
    client_id: Optional[int] = Field(None, description="Identifiant du client")
    card_id: Optional[int] = Field(None, description="Identifiant de la carte")
    merchant_id: Optional[int] = Field(None, description="Identifiant du marchand")
    merchant_state: Optional[str] = Field(None, description="État du marchand")
    mcc: Optional[int] = Field(None, description="Merchant Category Code")


class StatsOverview(BaseModel):
    """
    Vue d'ensemble des statistiques globales.

    Attributes
    ----------
    total_transactions : int
        Nombre total de transactions
    fraud_rate : float
        Taux de fraude
    avg_amount : float
        Montant moyen des transactions
    most_common_type : str
        Type de transaction le plus fréquent
    """

    total_transactions: int = Field(..., description="Nombre total de transactions")
    fraud_rate: float = Field(..., ge=0, le=1, description="Taux de fraude")
    avg_amount: float = Field(..., description="Montant moyen")
    most_common_type: str = Field(..., description="Type le plus fréquent")


class AmountDistribution(BaseModel):
    """
    Distribution des montants par classe.

    Attributes
    ----------
    bins : List[str]
        Classes de montants
    counts : List[int]
        Nombre de transactions par classe
    """

    bins: List[str] = Field(..., description="Classes de montants")
    counts: List[int] = Field(..., description="Nombre par classe")


class TypeStats(BaseModel):
    """
    Statistiques par type de transaction.

    Attributes
    ----------
    type : str
        Type de transaction
    count : int
        Nombre de transactions
    avg_amount : float
        Montant moyen
    total_amount : float
        Montant total
    """

    type: str = Field(..., description="Type de transaction")
    count: int = Field(..., description="Nombre de transactions")
    avg_amount: float = Field(..., description="Montant moyen")
    total_amount: float = Field(..., description="Montant total")


class DailyStats(BaseModel):
    """
    Statistiques quotidiennes.

    Attributes
    ----------
    step : int
        Jour (step)
    count : int
        Nombre de transactions
    avg_amount : float
        Montant moyen
    total_amount : float
        Volume total
    """

    step: int = Field(..., description="Jour (step)")
    count: int = Field(..., description="Nombre de transactions")
    avg_amount: float = Field(..., description="Montant moyen")
    total_amount: float = Field(..., description="Volume total")


class FraudSummary(BaseModel):
    """
    Résumé de la fraude.

    Attributes
    ----------
    total_frauds : int
        Nombre total de fraudes
    flagged : int
        Nombre de fraudes signalées
    precision : float
        Précision de détection
    recall : float
        Rappel de détection
    """

    total_frauds: int = Field(..., description="Nombre total de fraudes")
    flagged: int = Field(..., description="Nombre de fraudes signalées")
    precision: float = Field(..., ge=0, le=1, description="Précision")
    recall: float = Field(..., ge=0, le=1, description="Rappel")


class FraudByType(BaseModel):
    """
    Fraude par type de transaction.

    Attributes
    ----------
    type : str
        Type de transaction
    fraud_count : int
        Nombre de fraudes
    total_count : int
        Nombre total de transactions
    fraud_rate : float
        Taux de fraude
    """

    type: str = Field(..., description="Type de transaction")
    fraud_count: int = Field(..., description="Nombre de fraudes")
    total_count: int = Field(..., description="Nombre total")
    fraud_rate: float = Field(..., ge=0, le=1, description="Taux de fraude")


class FraudPredictionRequest(BaseModel):
    """
    Requête de prédiction de fraude.

    Attributes
    ----------
    amount : float
        Montant de la transaction
    use_chip : Optional[str]
        Type d'utilisation (Chip/Swipe/Online)
    merchant_state : str
        État du marchand
    mcc : int
        Merchant Category Code
    """

    amount: float = Field(..., ge=0, description="Montant")
    use_chip: Optional[str] = Field(None, description="Type d'utilisation")
    merchant_state: str = Field(..., description="État du marchand")
    mcc: int = Field(..., description="Merchant Category Code")


class FraudPredictionResponse(BaseModel):
    """
    Réponse de prédiction de fraude.

    Attributes
    ----------
    isFraud : bool
        Prédiction de fraude
    probability : float
        Probabilité de fraude
    """

    isFraud: bool = Field(..., description="Prédiction de fraude")
    probability: float = Field(..., ge=0, le=1, description="Probabilité de fraude")


class Customer(BaseModel):
    """
    Modèle représentant un client.

    Attributes
    ----------
    id : int
        Identifiant unique du client
    transactions_count : int
        Nombre de transactions
    avg_amount : float
        Montant moyen des transactions
    total_amount : float
        Montant total des transactions
    fraudulent : bool
        Indicateur si le client a été impliqué dans une fraude
    """

    id: int = Field(..., description="Identifiant client")
    transactions_count: int = Field(..., description="Nombre de transactions")
    avg_amount: float = Field(..., description="Montant moyen")
    total_amount: float = Field(..., description="Montant total")
    fraudulent: bool = Field(..., description="Impliqué dans une fraude")


class CustomerListResponse(BaseModel):
    """
    Réponse paginée pour les clients.

    Attributes
    ----------
    page : int
        Numéro de page
    limit : int
        Nombre d'éléments par page
    total : int
        Nombre total de clients
    customers : List[int]
        Liste des identifiants clients
    """

    page: int = Field(..., description="Numéro de page")
    limit: int = Field(..., description="Nombre d'éléments par page")
    total: int = Field(..., description="Nombre total de clients")
    customers: List[int] = Field(..., description="Liste des identifiants clients")


class SystemHealth(BaseModel):
    """
    État de santé du système.

    Attributes
    ----------
    status : str
        Statut du système (ok, degraded, error)
    uptime : str
        Temps de fonctionnement
    dataset_loaded : bool
        Indicateur de chargement des données
    timestamp : str
        Horodatage de la vérification
    """

    status: str = Field(..., description="Statut du système")
    uptime: str = Field(..., description="Temps de fonctionnement")
    dataset_loaded: bool = Field(..., description="Données chargées")
    timestamp: str = Field(..., description="Horodatage")


class SystemMetadata(BaseModel):
    """
    Métadonnées du système.

    Attributes
    ----------
    version : str
        Version de l'API
    last_update : str
        Date de dernière mise à jour
    total_transactions : int
        Nombre total de transactions dans le dataset
    data_source : str
        Source des données
    """

    version: str = Field(..., description="Version de l'API")
    last_update: str = Field(..., description="Dernière mise à jour")
    total_transactions: int = Field(..., description="Nombre de transactions")
    data_source: str = Field(..., description="Source des données")


class ErrorResponse(BaseModel):
    """
    Réponse d'erreur standardisée.

    Attributes
    ----------
    error : str
        Type d'erreur
    message : str
        Message d'erreur détaillé
    details : Optional[Dict[str, Any]]
        Détails supplémentaires
    """

    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message d'erreur")
    details: Optional[Dict[str, Any]] = Field(None, description="Détails")
