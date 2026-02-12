import pandas as pd
from typing import Dict, Any, Optional
from app.core.config import settings

def get_all_customers(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """
    Retourne la liste des clients (table users_data) avec pagination.
    """
    users = settings.get_users()
    
    total = len(users)
    start = (page - 1) * limit
    end = start + limit
    
    # Nettoyage des NaN pour le JSON
    subset = users.iloc[start:end].fillna("").to_dict(orient="records")
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "customers": subset
    }

def get_customer_profile(client_id: int) -> Optional[Dict[str, Any]]:
    """
    Jointure critique : Users (Profil) + Transactions (Comportement).
    """
    users = settings.get_users()
    df_tx = settings.get_df()
    
    # 1. Récupération du Profil Client
    # On cherche dans la colonne 'id' du fichier users_data
    user_row = users[users['id'] == client_id]
    
    if user_row.empty:
        return None # Client introuvable
        
    user_data = user_row.iloc[0].fillna("").to_dict()
    
    # 2. Récupération de ses Transactions (La Jointure)
    # On cherche dans la colonne 'client_id' du fichier transactions_data
    if 'client_id' in df_tx.columns:
        client_txs = df_tx[df_tx['client_id'] == client_id]
    else:
        # Fallback de sécurité (au cas où la colonne s'appellerait autrement)
        client_txs = pd.DataFrame()

    # 3. Calcul des Statistiques (Analytics)
    if not client_txs.empty:
        # Nettoyage supplémentaire au cas où il reste des symboles '$' ou '()'
        # On force la conversion en numérique 
        if client_txs['amount'].dtype == object:
             amounts = client_txs['amount'].astype(str).str.replace(r'[\$,()]', '', regex=True).astype(float)
        else:
             amounts = client_txs['amount']

        total_spent = amounts.sum()
        tx_count = len(client_txs)
        avg_basket = total_spent / tx_count if tx_count > 0 else 0
        fraud_history = client_txs['isFraud'].sum()
    else:
        total_spent = 0.0
        tx_count = 0
        avg_basket = 0.0
        fraud_history = 0

    return {
        "profile": {
            "id": user_data.get("id"),
            "full_name": f"Client {user_data.get('id')}", # Anonymisé car pas de nom dans le CSV
            "age": user_data.get("current_age"),
            "income": user_data.get("yearly_income"),
            "credit_score": user_data.get("credit_score"),
            "address": user_data.get("address")
        },
        "financial_stats": {
            "total_spent_lifetime": round(total_spent, 2),
            "transaction_count": int(tx_count),
            "average_basket": round(avg_basket, 2),
            "fraud_incidents": int(fraud_history)
        }
    }

def get_top_customers(n: int = 10) -> list[Dict[str, Any]]:
    """
    Retourne les N plus gros clients en volume de transactions.
    CORRIGÉ pour utiliser la colonne 'client_id'.
    """
    df_tx = settings.get_df()
    
    # 1. Sécurité : DataFrame vide ?
    if df_tx.empty:
        return []

    # 2. Vérification de la colonne
    target_col = 'client_id'
    
    if target_col not in df_tx.columns:
        # Fallback au cas où (si jamais le header change)
        print(f"ERREUR: Colonne '{target_col}' introuvable. Colonnes dispos: {list(df_tx.columns)}")
        return []

    # 3. Calcul du Top N
    # On compte combien de fois chaque 'client_id' apparaît
    top_users = df_tx[target_col].value_counts().head(n)
    
    results = []
    for client, count in top_users.items():
        results.append({
            "client_id": int(client),  # Conversion en int pour être propre
            "total_transactions": int(count),
            "rank": len(results) + 1
        })
        
    return results