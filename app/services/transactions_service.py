import pandas as pd
from typing import List, Dict, Any, Optional
from app.core.config import settings

# --- UTILITAIRE DE NETTOYAGE ---
def _clean_amount_column(df):
    """Nettoie la colonne montant pour les comparaisons."""
    if pd.api.types.is_numeric_dtype(df['amount']):
        return df['amount']
    # Enlève $, (), et convertit
    return df['amount'].astype(str).str.replace(r'[\$,()]', '', regex=True).astype(float)

# --- ROUTE 1 : PAGINATION ---
def get_paginated_transactions(page: int, limit: int, tx_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Récupère une liste de transactions avec pagination et filtrage.
    """
    df = settings.get_df()
    
    # 1. Filtrage par type (ou use_chip selon ton fichier)
    filtered_df = df
    if tx_type:
        col_type = 'type' if 'type' in df.columns else 'use_chip'
        if col_type in df.columns:
            filtered_df = df[df[col_type] == tx_type]

    # 2. Pagination
    total_count = len(filtered_df)
    start = (page - 1) * limit
    end = start + limit
    
    # 3. Extraction et Nettoyage
    subset = filtered_df.iloc[start:end]
    
    # On remplace les NaN par None pour le JSON
    transactions = subset.where(pd.notnull(subset), None).to_dict(orient="records")
    
    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "transactions": transactions
    }

# --- ROUTE 2 : DÉTAIL PAR ID ---
def get_transaction_by_id(tx_id: int) -> Optional[Dict[str, Any]]:
    """Cherche une transaction par son ID unique."""
    df = settings.get_df()
    
    # Recherche dans la colonne 'id'
    if 'id' not in df.columns: return None
    
    row = df[df['id'] == tx_id]
    if row.empty:
        return None
        
    # Conversion propre
    return row.iloc[0].where(pd.notnull(row.iloc[0]), None).to_dict()

# --- ROUTE 4 : LISTE DES TYPES ---
def get_transaction_types() -> List[str]:
    """Liste les types uniques (ex: Swipe, Online)."""
    df = settings.get_df()
    
    col_type = 'type'
    if 'type' not in df.columns:
        if 'use_chip' in df.columns:
            col_type = 'use_chip'
        else:
            return []
            
    return df[col_type].dropna().unique().tolist()

# --- ROUTE 5 : RÉCENTES ---
def get_recent_transactions(limit: int) -> List[Dict[str, Any]]:
    """Renvoie les dernières transactions du fichier."""
    df = settings.get_df()
    # On prend la fin du fichier et on inverse l'ordre
    subset = df.tail(limit).iloc[::-1]
    return subset.where(pd.notnull(subset), None).to_dict(orient="records")

# --- ROUTE 3 : RECHERCHE MULTICRITÈRE ---
def search_transactions(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filtre les transactions selon plusieurs critères."""
    df = settings.get_df()
    if df.empty: return []

    # 1. Filtre par Type
    if 'type' in criteria:
        col = 'type' if 'type' in df.columns else 'use_chip'
        df = df[df[col] == criteria['type']]
    
    # 2. Filtre par Montant (Min/Max)
    # Attention, il faut nettoyer la colonne montant avant de comparer
    if 'min_amount' in criteria or 'max_amount' in criteria:
        # On crée une série temporaire propre pour le filtre
        clean_amounts = _clean_amount_column(df)
        
        if 'min_amount' in criteria:
            df = df[clean_amounts >= criteria['min_amount']]
            clean_amounts = clean_amounts[clean_amounts >= criteria['min_amount']] # Alignement
            
        if 'max_amount' in criteria:
            df = df[clean_amounts <= criteria['max_amount']]

    # 3. Filtre Fraude
    if 'isFraud' in criteria and 'isFraud' in df.columns:
        df = df[df['isFraud'] == criteria['isFraud']]

    # On renvoie max 50 résultats pour ne pas surcharger
    return df.head(50).where(pd.notnull(df), None).to_dict(orient="records")

# --- ROUTE 7 : PAR CLIENT ---
def get_transactions_by_customer(client_id: int) -> List[Dict[str, Any]]:
    """Transactions d'un client spécifique."""
    df = settings.get_df()
    if 'client_id' not in df.columns: return []
    
    subset = df[df['client_id'] == client_id].head(100)
    return subset.where(pd.notnull(subset), None).to_dict(orient="records")

# --- ROUTE 8 : PAR MARCHAND ---
def get_transactions_to_merchant(merchant_id: int) -> List[Dict[str, Any]]:
    """Transactions reçues par un marchand."""
    df = settings.get_df()
    if 'merchant_id' not in df.columns: return []
    
    subset = df[df['merchant_id'] == merchant_id].head(100)
    return subset.where(pd.notnull(subset), None).to_dict(orient="records")

# --- ROUTE 6 : SUPPRESSION (SIMULATION) ---
def delete_transaction(tx_id: int) -> bool:
    """Vérifie juste si l'ID existe pour simuler la suppression."""
    df = settings.get_df()
    if 'id' not in df.columns: return False
    
    exists = not df[df['id'] == tx_id].empty
    return exists