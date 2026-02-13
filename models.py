from pydantic import BaseModel
from typing import List, Optional


class Transaction(BaseModel):
    """
    Modèle de données pour la recherche multicritère (Route 3).
    """
    type: Optional[str] = None
    """Modèle représentant une transaction (Typage obligatoire)."""
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    isFraud: int
    isFlaggedFraud: int


class TransactionSearch(BaseModel):
    """Modèle pour la recherche multicritère (Route 3)."""
    type: Optional[str] = None
    isFraud: Optional[int] = None
    amount_range: Optional[List[float]] = None
