"""Routes pour les transactions."""

from typing import Dict
from fastapi import APIRouter, HTTPException

from banking_api.services.data_cache import get_cached_dataframe, get_indexed_dataframe

router = APIRouter()


@router.get("/by-customer/{customer_id}", response_model=dict)
def get_transactions_by_customer(customer_id: str, limit: int = 100) -> dict:
    """
    Récupère les transactions d'un client spécifique (optimisé avec index).

    Args:
        customer_id: ID du client
        limit: Nombre maximum de transactions à retourner

    Returns:
        dict: Liste des transactions du client
    """
    df_indexed = get_indexed_dataframe()

    try:
        customer_transactions = df_indexed.loc[[int(customer_id)]].head(limit)
    except KeyError:
        customer_transactions = df_indexed.iloc[0:0]  # DataFrame vide si client n'existe pas

    transactions = [
        {
            "id": str(row["id"]),
            "date": str(row["date"]),
            "amount": float(row["amount"]),
            "merchant_id": str(row["merchant_id"]),
            "merchant_city": str(row["merchant_city"]),
            "use_chip": str(row["use_chip"]),
            "isFraud": int(row["isFraud"])
        }
        for _, row in customer_transactions.iterrows()
    ]

    return {"transactions": transactions, "count": len(transactions)}