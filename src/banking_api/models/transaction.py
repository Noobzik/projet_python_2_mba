from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class TransactionOut(BaseModel):
    """
    Transaction exposed by the API.

    Notes
    -----
    - `id` is generated from the dataset row index when the dataset has no explicit ID column.
    - Only a subset of fields is exposed to keep the contract stable.
    """

    id: str = Field(..., examples=["tx_0000001"])
    amount: float = Field(..., ge=0, examples=[500.0])
    type: str = Field(..., examples=["CASH_OUT", "TRANSFER"])
    isFraud: Optional[bool] = Field(default=None, examples=[False])
    nameOrig: Optional[str] = Field(default=None, examples=["C1231006815"])
    nameDest: Optional[str] = Field(default=None, examples=["C9876543210"])

    @classmethod
    def from_row(cls, row_index: int, row: dict[str, Any]) -> "TransactionOut":
        tx_id = f"tx_{row_index:07d}"
        amount = float(row.get("amount", 0.0))
        tx_type = str(row.get("type", "UNKNOWN"))
        is_fraud_val = row.get("isFraud", None)

        is_fraud: Optional[bool]
        if is_fraud_val is None:
            is_fraud = None
        elif str(is_fraud_val).isdigit():
            is_fraud = bool(int(is_fraud_val))
        else:
            is_fraud = bool(is_fraud_val)

        return cls(
            id=tx_id,
            amount=amount,
            type=tx_type,
            isFraud=is_fraud,
            nameOrig=row.get("nameOrig", None),
            nameDest=row.get("nameDest", None),
        )


class TransactionListOut(BaseModel):
    page: int
    transactions: list[TransactionOut]
