import pandas as pd
from typing import Dict, Any, List
from app.core.config import settings

def get_fraud_dashboard() -> Dict[str, Any]:
    """
    Vue d'ensemble de la fraude pour le tableau de bord sécurité.
    """
    df = settings.get_df()
    
    # On filtre uniquement les fraudes
    frauds = df[df['isFraud'] == 1]
    
    total_fraud_amt = frauds['amount'].sum()
    total_cases = len(frauds)
    
    # Top 3 des villes touchées par la fraude
    # On utilise 'merchant_city'
    if 'merchant_city' in frauds.columns:
        top_cities = frauds['merchant_city'].value_counts().head(3).to_dict()
    else:
        top_cities = {}

    return {
        "summary": {
            "total_loss": round(total_fraud_amt, 2),
            "total_cases": total_cases,
            "avg_loss_per_case": round(total_fraud_amt / total_cases, 2) if total_cases > 0 else 0
        },
        "hotspots": top_cities
    }

def get_highest_frauds(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retourne la liste des plus grosses fraudes détectées, triées par montant.
    """
    df = settings.get_df()
    
    # 1. Filtre Fraude
    frauds = df[df['isFraud'] == 1].copy()
    
    # 2. Tri par montant décroissant
    top_frauds = frauds.sort_values(by='amount', ascending=False).head(limit)
    
    # 3. Nettoyage pour JSON (NaN -> None)
    # On sélectionne les colonnes intéressantes
    columns_to_keep = ['id', 'date', 'amount', 'client_id', 'merchant_city', 'merchant_state', 'type']
    # On s'assure que les colonnes existent
    available_cols = [c for c in columns_to_keep if c in top_frauds.columns]
    
    result = top_frauds[available_cols].fillna("").to_dict(orient="records")
    return result
# --- AJOUTER À LA FIN DE app/services/fraud_detection_service.py ---

def get_frauds_by_type() -> list[Dict[str, Any]]:
    """
    Groupe les fraudes par type de transaction (ou par Merchant City si 'type' absent).
    """
    df = settings.get_df()
    if df.empty: 
        return []

    # 1. On essaie de trouver une colonne 'type' ou équivalent
    # Dans ton Excel, c'est peut-être 'use_chip' ou 'mcc'
    col_type = 'type'
    if 'type' not in df.columns:
        if 'use_chip' in df.columns:
            col_type = 'use_chip'
        elif 'mcc' in df.columns:
            col_type = 'mcc'
        else:
            return [{"error": "Colonne Type introuvable"}]

    # 2. On filtre les fraudes (Si la colonne isFraud existe, sinon on simule)
    if 'isFraud' in df.columns:
        frauds = df[df['isFraud'] == 1]
    elif 'errors' in df.columns:
        # On considère qu'une erreur non vide est une fraude potentielle
        frauds = df[df['errors'].notna() & (df['errors'] != "")]
    else:
        # Fallback pour la démo si pas de colonne fraude explicite
        # On prend les gros montants comme "fraude simulée"
        frauds = df[df['amount'] > 500] 

    if frauds.empty:
        return [{"message": "Aucune fraude détectée pour le moment"}]

    # 3. Agrégation
    stats = frauds[col_type].value_counts().reset_index()
    stats.columns = ['type', 'count']
    
    return stats.to_dict(orient="records")

def predict_fraud_score(data) -> Dict[str, Any]:
    """
    Algorithme de Scoring (Règle métier simplifiée pour le projet).
    """
    # Règle 1 : Montant excessif (> 10,000)
    risk_score = 0.0
    reasons = []

    if data.amount > 10000:
        risk_score += 0.4
        reasons.append("Montant très élevé")
    
    # Règle 2 : Vidage de compte (Solde passe à 0)
    if data.oldbalanceOrg > 0 and data.newbalanceOrig == 0:
        risk_score += 0.5
        reasons.append("Vidage complet du compte")

    # Règle 3 : Type suspect (Si c'est 'Online' par exemple)
    if "Online" in data.type: # Adapté à ton Excel qui a "Online Transaction"
        risk_score += 0.1

    # Normalisation (Max 1.0)
    risk_score = min(risk_score, 0.99)
    is_fraud = risk_score > 0.5

    return {
        "isFraud": is_fraud,
        "probability": round(risk_score, 2),
        "alert_level": "CRITICAL" if is_fraud else "LOW",
        "reasons": reasons
    }