"""Transaction data models.

This module defines Pydantic models for transaction data validation
and serialization.
"""

from datetime import datetime
from typing import Optional, List, Any
import pandas as pd
from pydantic import BaseModel, Field, field_validator


class Transaction(BaseModel):
    """Transaction model representing a banking transaction.

    Parameters
    ----------
    id : str
        Unique transaction identifier.
    date : datetime
        Transaction date and time.
    client_id : int
        Customer ID who made the transaction.
    card_id : int
        Card ID used for the transaction.
    amount : float
        Amount of the transaction.
    use_chip : str
        Whether chip was used (Swipe Transaction, Chip Transaction, Online Transaction).
    merchant_id : int
        Merchant identifier.
    merchant_city : str
        City of the merchant.
    merchant_state : str
        State of the merchant.
    zip : Optional[float]
        ZIP code of the merchant.
    mcc : int
        Merchant Category Code.
    errors : Optional[str]
        Transaction errors if any.
    isFraud : int
        Whether the transaction is fraudulent (1) or not (0).
    """

    id: str
    date: datetime
    client_id: int
    card_id: int
    amount: float
    use_chip: Optional[str] = "Unknown"
    merchant_id: int
    merchant_city: Optional[str] = None
    merchant_state: Optional[str] = None
    zip: Optional[float] = None
    mcc: int
    errors: Optional[str] = None
    isFraud: int = Field(0, ge=0, le=1)

    @field_validator('amount', mode='before')
    @classmethod
    def parse_amount(cls, v: str) -> float:
        """Parse amount from string format with dollar sign.

        Parameters
        ----------
        v : str
            Amount value (may include $ sign).

        Returns
        -------
        float
            Parsed amount value.
        """
        if isinstance(v, str):
            # Remove $ sign and convert to float
            return float(v.replace('$', '').replace(',', ''))
        return float(v)

    @field_validator('errors', 'merchant_city', 'merchant_state', mode='before')
    @classmethod
    def parse_optional_string_fields(cls, v: Any) -> Optional[str]:
        """Parse optional string fields, handling NaN values.

        Parameters
        ----------
        v : Any
            String value (may be NaN, empty string, or actual value).

        Returns
        -------
        Optional[str]
            Parsed string value or None.
        """
        if pd.isna(v) or v == '' or v is None:
            return None
        return str(v)

    @field_validator('use_chip', mode='before')
    @classmethod
    def parse_use_chip(cls, v: Any) -> Optional[str]:
        """Parse use_chip field, providing default for NaN.

        Parameters
        ----------
        v : Any
            Use chip value.

        Returns
        -------
        Optional[str]
            Parsed use_chip value or default.
        """
        if pd.isna(v) or v == '' or v is None:
            return "Unknown"
        return str(v)

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "7475327",
                "date": "2010-01-01 00:01:00",
                "client_id": 1556,
                "card_id": 2972,
                "amount": -77.00,
                "use_chip": "Swipe Transaction",
                "merchant_id": 59935,
                "merchant_city": "Beulah",
                "merchant_state": "ND",
                "zip": 58523.0,
                "mcc": 5499,
                "errors": "",
                "isFraud": 0
            }
        }


class TransactionList(BaseModel):
    """Paginated list of transactions.

    Parameters
    ----------
    page : int
        Current page number.
    limit : int
        Number of items per page.
    total : int
        Total number of transactions.
    transactions : List[Transaction]
        List of transaction objects.
    """

    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    transactions: List[Transaction]


class TransactionSearch(BaseModel):
    """Search criteria for transactions.

    Parameters
    ----------
    use_chip : Optional[str]
        Filter by transaction method (Swipe, Chip, Online).
    isFraud : Optional[int]
        Filter by fraud status (0 or 1).
    amount_range : Optional[List[float]]
        Filter by amount range [min, max].
    client_id : Optional[int]
        Filter by customer ID.
    merchant_state : Optional[str]
        Filter by merchant state.
    merchant_city : Optional[str]
        Filter by merchant city.
    """

    use_chip: Optional[str] = None
    isFraud: Optional[int] = Field(None, ge=0, le=1)
    amount_range: Optional[List[float]] = None
    client_id: Optional[int] = None
    merchant_state: Optional[str] = None
    merchant_city: Optional[str] = None

    @field_validator('amount_range')
    @classmethod
    def validate_amount_range(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate amount range.

        Parameters
        ----------
        v : Optional[List[float]]
            Amount range [min, max].

        Returns
        -------
        Optional[List[float]]
            Validated amount range.

        Raises
        ------
        ValueError
            If range format is invalid.
        """
        if v is not None and len(v) != 2:
            raise ValueError('amount_range must contain exactly 2 values')
        if v is not None and v[0] > v[1]:
            raise ValueError('amount_range min must be <= max')
        return v


class FraudPredictionRequest(BaseModel):
    """Request model for fraud prediction.

    Parameters
    ----------
    amount : float
        Transaction amount.
    use_chip : str
        Transaction method (Swipe, Chip, Online).
    merchant_state : str
        Merchant state.
    mcc : int
        Merchant Category Code.
    """

    amount: float
    use_chip: str
    merchant_state: str
    mcc: int


class FraudPredictionResponse(BaseModel):
    """Response model for fraud prediction.

    Parameters
    ----------
    isFraud : bool
        Whether the transaction is predicted as fraudulent.
    probability : float
        Fraud probability score (0-1).
    """

    isFraud: bool
    probability: float = Field(..., ge=0.0, le=1.0)
