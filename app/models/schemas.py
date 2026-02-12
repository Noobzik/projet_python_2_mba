from pydantic import BaseModel, Field
from typing import Optional

# 1. Schéma de base pour une Transaction
class Transaction(BaseModel):
    id: int
    amount: float
    isFraud: int
    type: str  # Provient de notre mapping (use_chip)
    
    # Champs optionnels
    date: Optional[str] = None
    client_id: Optional[int] = None
    card_id: Optional[int] = None
    merchant_id: Optional[int] = None
    merchant_city: Optional[str] = None
    mcc: Optional[int] = None
    errors: Optional[str] = None

    class Config:
        from_attributes = True

# 2. Schéma pour la Pagination
class PaginatedTransactions(BaseModel):
    total: int
    page: int
    limit: int
    transactions: list[Transaction]