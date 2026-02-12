"""Modèles de transactions et schémas Pydantic.

Ce module définit tous les modèles de données et schémas de validation
pour les opérations liées aux transactions.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Transaction(BaseModel):
    """Modèle principal de transaction.

    Attributes
    ----------
    step : int
        Étape temporelle dans la simulation
    type : str
        Type de transaction (PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN)
    amount : float
        Montant de la transaction
    nameOrig : str
        Client initiant la transaction
    oldbalanceOrg : float
        Solde initial avant transaction (émetteur)
    newbalanceOrig : float
        Nouveau solde après transaction (émetteur)
    nameDest : str
        Client recevant la transaction
    oldbalanceDest : float
        Solde initial avant transaction (destinataire)
    newbalanceDest : float
        Nouveau solde après transaction (destinataire)
    isFraud : int
        Indicateur de fraude (0=légitime, 1=frauduleuse)
    isFlaggedFraud : int
        Indicateur signalé comme fraude par le système
    """

    step: int = Field(..., ge=0, description="Étape temporelle")
    type: str = Field(..., description="Type de transaction")
    amount: float = Field(..., ge=0, description="Montant de la transaction")
    nameOrig: str = Field(..., description="Identifiant du client émetteur")
    oldbalanceOrg: float = Field(..., ge=0, description="Ancien solde émetteur")
    newbalanceOrig: float = Field(..., ge=0, description="Nouveau solde émetteur")
    nameDest: str = Field(..., description="Identifiant du client destinataire")
    oldbalanceDest: float = Field(..., ge=0, description="Ancien solde destinataire")
    newbalanceDest: float = Field(..., ge=0, description="Nouveau solde destinataire")
    isFraud: int = Field(..., ge=0, le=1, description="Indicateur de fraude")
    isFlaggedFraud: int = Field(..., ge=0, le=1, description="Indicateur de fraude système")

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Valider le type de transaction.

        Parameters
        ----------
        v : str
            Valeur du type de transaction

        Returns
        -------
        str
            Type de transaction validé

        Raises
        ------
        ValueError
            Si le type ne fait pas partie des valeurs autorisées
        """
        allowed_types = {'PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT', 'CASH_IN'}
        if v not in allowed_types:
            raise ValueError("Invalid transaction type")
        return v


class TransactionSearchRequest(BaseModel):
    """Modèle de requête pour recherche multi-critères.

    Attributes
    ----------
    type : Optional[str]
        Filtrer par type de transaction
    isFraud : Optional[int]
        Filtrer par statut de fraude
    amount_range : Optional[tuple[float, float]]
        Filtrer par intervalle de montant [min, max]
    customer_id : Optional[str]
        Filtrer par identifiant client
    """

    type: Optional[str] = Field(None, description="Filtre par type de transaction")
    isFraud: Optional[int] = Field(None, ge=0, le=1, description="Filtre fraude")
    amount_range: Optional[list[float]] = Field(
        None, description="Intervalle de montant [min, max]")
    customer_id: Optional[str] = Field(None, description="Filtre identifiant client")


class TransactionResponse(BaseModel):
    """Modèle de réponse pour une transaction unique.

    Attributes
    ----------
    id : str
        Identifiant unique de la transaction
    step : int
        Étape temporelle
    type : str
        Type de transaction
    amount : float
        Montant de la transaction
    nameOrig : str
        Client émetteur
    newbalanceOrig : float
        Nouveau solde émetteur
    nameDest : str
        Client destinataire
    newbalanceDest : float
        Nouveau solde destinataire
    isFraud : int
        Indicateur de fraude
    """

    id: str
    step: int
    type: str
    amount: float
    nameOrig: str
    newbalanceOrig: float
    nameDest: str
    newbalanceDest: float
    isFraud: int


class TransactionListResponse(BaseModel):
    """Modèle de réponse pour liste paginée de transactions.

    Attributes
    ----------
    page : int
        Numéro de page courant
    limit : int
        Nombre d’éléments par page
    total : int
        Nombre total de transactions
    transactions : list[TransactionResponse]
        Liste des transactions
    """

    page: int
    limit: int
    total: int
    transactions: list[TransactionResponse]
