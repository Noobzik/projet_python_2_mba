from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from banking_api.models.transaction import TransactionListOut, TransactionOut

from banking_api.models.search import TransactionSearchIn

from banking_api.services.transactions_service import (
    get_recent_transactions,
    get_transaction_by_id,
    get_transaction_types,
    list_transactions,
    delete_transaction_fake,
    search_transactions,
    get_transactions_by_customer,
    get_transactions_to_customer,

)


router = APIRouter()


@router.get("/transactions", response_model=TransactionListOut)
def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    type: Optional[str] = Query(None),
    isFraud: Optional[bool] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
) -> TransactionListOut:
    try:
        return list_transactions(
            page=page,
            limit=limit,
            tx_type=type,
            is_fraud=isFraud,
            min_amount=min_amount,
            max_amount=max_amount,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/transactions/types", response_model=list[str])
def list_transaction_types() -> list[str]:
    try:
        return get_transaction_types()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/transactions/recent", response_model=list[TransactionOut])
def recent_transactions(n: int = Query(10, ge=1, le=100)) -> list[TransactionOut]:
    try:
        return get_recent_transactions(n=n)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/transactions/by-customer/{customer_id}", response_model=list[TransactionOut])
def by_customer(customer_id: str) -> list[TransactionOut]:
    try:
        return get_transactions_by_customer(customer_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/transactions/to-customer/{customer_id}", response_model=list[TransactionOut])
def to_customer(customer_id: str) -> list[TransactionOut]:
    try:
        return get_transactions_to_customer(customer_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/transactions/{id}", response_model=TransactionOut)
def get_transaction(id: str) -> TransactionOut:
    try:
        return get_transaction_by_id(id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/transactions/search", response_model=list[TransactionOut])
def search(criteria: TransactionSearchIn) -> list[TransactionOut]:
    try:
        return search_transactions(criteria)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/transactions/{id}", status_code=204)
def delete_transaction(id: str) -> None:
    if os.getenv("APP_ENV", "dev").lower() != "test":
        raise HTTPException(status_code=403, detail="DELETE is only allowed in test mode")

    try:
        delete_transaction_fake(id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
