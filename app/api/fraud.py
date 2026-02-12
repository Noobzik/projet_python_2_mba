from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from app.services import fraud_detection_service

router = APIRouter()

# --- Modèle de données pour la Prédiction (Validation) ---
class PredictionInput(BaseModel):
    type: str = Field(..., description="Type de transaction (ex: ONLINE, TRANSFER)")
    amount: float = Field(..., gt=0, description="Montant de la transaction")
    oldbalanceOrg: float = Field(0, description="Solde avant transaction")
    newbalanceOrig: float = Field(0, description="Solde après transaction")

# --- ROUTES ---

@router.get("/summary", summary="Route 13: Dashboard Fraude")
def get_fraud_summary() -> Dict[str, Any]:
    """KPIs globaux sur la fraude bancaire (Total, Taux, etc.)."""
    return fraud_detection_service.get_fraud_dashboard()

@router.get("/highest", summary="Top Transactions Frauduleuses")
def get_top_frauds(limit: int = 10) -> List[Dict[str, Any]]:
    """Liste des fraudes les plus coûteuses."""
    return fraud_detection_service.get_highest_frauds(limit)

@router.get("/by-type", summary="Route 14: Fraude par Type")
def get_fraud_by_type() -> List[Dict[str, Any]]:
    """
    Répartition du volume de fraude par type de transaction (ex: CASH_OUT vs TRANSFER).
    """
    return fraud_detection_service.get_frauds_by_type()

@router.post("/predict", summary="Route 15: Scoring (Machine Learning)")
def predict_fraud(data: PredictionInput) -> Dict[str, Any]:
    """
    Simule un modèle de Machine Learning pour prédire le risque.
    Retourne la probabilité de fraude.
    """
    return fraud_detection_service.predict_fraud_score(data)