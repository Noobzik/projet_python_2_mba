from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel  # <--- Ajout nécessaire pour le body JSON

from banking_api.models.fraud import FraudSummaryOut, FraudTopCustomersOut, FraudTransactionListOut

from banking_api.services.fraud_service import (
    fraud_summary,
    list_fraud_transactions,
    top_fraud_customers,
)

router = APIRouter()

# --- MODÈLE POUR LA PRÉDICTION (Route 15) ---
class TransactionFeatures(BaseModel):
    type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float

# --- ROUTE 15 : PRÉDICTION DE FRAUDE (SCORING) ---
@router.post("/fraud/predict")
def predict_fraud(features: TransactionFeatures):
    """
    Simule une prédiction de fraude basée sur des règles métiers.
    Retourne une probabilité et un verdict booléen.
    """
    probability = 0.0
    
    # Règle 1 : Les gros montants sont suspects
    if features.amount > 200000:
        probability += 0.4
    
    # Règle 2 : Vider entièrement son compte est suspect (surtout en transfert)
    if features.oldbalanceOrg > 0 and features.newbalanceOrig == 0:
        probability += 0.5
        
    # Règle 3 : Certains types sont plus risqués
    if features.type.upper() in ["TRANSFER", "CASH_OUT"]:
        probability += 0.1

    # On plafonne la probabilité à 99%
    probability = min(probability, 0.99)
    
    # Verdict : Si proba > 75%, c'est une fraude
    is_fraud = probability > 0.75

    return {
        "isFraud": is_fraud,
        "probability": round(probability, 2),
        "risk_level": "CRITICAL" if is_fraud else "LOW"
    }

# --- ROUTES EXISTANTES (Ne pas toucher) ---

@router.get("/fraud/summary", response_model=FraudSummaryOut)
def summary() -> FraudSummaryOut:
    try:
        return fraud_summary()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/fraud/transactions", response_model=FraudTransactionListOut)
def fraud_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> FraudTransactionListOut:
    try:
        return list_fraud_transactions(page=page, limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/fraud/top-customers", response_model=FraudTopCustomersOut)
def fraud_top_customers(n: int = Query(10, ge=1, le=100)) -> FraudTopCustomersOut:
    try:
        return top_fraud_customers(n=n)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e