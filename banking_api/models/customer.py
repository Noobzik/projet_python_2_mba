"""Modèles pour les clients."""

from typing import List

from pydantic import BaseModel, Field


class CustomerListResponse(BaseModel):
    """Liste paginée de clients."""

    page: int = Field(..., description="Numéro de la page actuelle")
    limit: int = Field(..., description="Nombre de clients par page")
    total: int = Field(..., description="Nombre total de clients")
    customers: List[int] = Field(..., description="Liste des identifiants clients")


class CustomerProfile(BaseModel):
    """Profil détaillé d'un client."""

    id: str = Field(..., description="Identifiant du client")
    transactions_count: int = Field(..., description="Nombre de transactions")
    avg_amount: float = Field(..., description="Montant moyen des transactions")
    total_amount: float = Field(..., description="Montant total des transactions")
    fraudulent: bool = Field(
        ..., description="Indique si le client a été impliqué dans une fraude"
    )
    fraud_count: int = Field(..., description="Nombre de fraudes")


class TopCustomer(BaseModel):
    """Client avec statistiques complètes."""

    customer_id: int = Field(..., description="Identifiant du client")
    transaction_count: int = Field(..., description="Nombre de transactions")
    total_amount: float = Field(..., description="Montant total des transactions")
    avg_amount: float = Field(..., description="Montant moyen des transactions")
    fraud_count: int = Field(..., description="Nombre de fraudes")
    fraudulent: bool = Field(
        ..., description="Indique si le client a commis des fraudes"
    )
