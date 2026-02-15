from pydantic import BaseModel


class Transaction(BaseModel):
    """
    Modèle représentant une transaction bancaire.
    Style numpy pour la documentation.
    """

    id: str
    amount: float
    type: str
    isFraud: int
    nameOrig: str
    nameDest: str
