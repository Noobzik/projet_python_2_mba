import pandas as pd
from typing import Dict, Any, List
from app.core.config import settings

# --- FONCTION UTILITAIRE (Pour nettoyer les montants "$77.00") ---
def _clean_amount_column(df):
    """Nettoie la colonne montant (enlève les $, (), et convertit en float)."""
    # Si c'est déjà numérique, on ne touche à rien
    if pd.api.types.is_numeric_dtype(df['amount']):
        return df['amount']
    
    # Sinon on nettoie les symboles $, (, ) et on convertit
    return df['amount'].astype(str).str.replace(r'[\$,()]', '', regex=True).astype(float)

# --- ROUTE 9 : KPI GLOBAUX ---
def get_global_stats() -> Dict[str, Any]:
    """
    Calcule les indicateurs macro-économiques.
    """
    df = settings.get_df()
    if df.empty: return {}
    
    # 1. Nettoyage et Calculs de base
    amounts = _clean_amount_column(df)
    total_tx = len(df)
    total_amount = amounts.sum()
    
    # 2. Gestion de la fraude (Compatible avec ton fichier)
    if 'isFraud' in df.columns:
        fraud_tx = df[df['isFraud'] == 1]
    elif 'errors' in df.columns:
        # On considère qu'une erreur non vide est une anomalie
        fraud_tx = df[df['errors'].notna() & (df['errors'] != "")]
    else:
        fraud_tx = pd.DataFrame()
    
    fraud_count = len(fraud_tx)
    
    # Calcul montant fraude (attention au format)
    if not fraud_tx.empty:
        # On nettoie aussi la colonne montant du sous-ensemble fraude
        fraud_amounts = _clean_amount_column(fraud_tx)
        fraud_amount_sum = fraud_amounts.sum()
    else:
        fraud_amount_sum = 0.0

    # 3. Extraction des Années (Ton code optimisé)
    min_year = None
    max_year = None
    if 'date' in df.columns:
        try:
            years = df['date'].astype(str).str.extract(r'(\d{4})').astype(float)
            if not years.empty:
                min_year = int(years.min().iloc[0])
                max_year = int(years.max().iloc[0])
        except Exception as e:
            print(f"Erreur extraction années: {e}")

    return {
        "volume": {
            "total_transactions": total_tx,
            "total_amount": round(total_amount, 2),
            "average_amount": round(amounts.mean(), 2)
        },
        "fraud": {
            "total_fraud_cases": fraud_count,
            "total_fraud_amount": round(fraud_amount_sum, 2),
            "fraud_rate_percent": round((fraud_count / total_tx) * 100, 3) if total_tx > 0 else 0
        },
        "time_span": {
            "min_year": min_year,
            "max_year": max_year
        }
    }

# --- ROUTE 11 : STATS PAR TYPE (Celle qui manquait !) ---
def get_stats_by_type() -> List[Dict[str, Any]]:
    """Répartition des transactions par méthode (Puce, Bande, En ligne)."""
    df = settings.get_df()
    if df.empty: return []

    # Adaptation à ton fichier : On utilise 'use_chip' (Swipe vs Online)
    # Si 'use_chip' n'existe pas, on cherche 'type'
    col_type = 'type'
    if 'type' not in df.columns and 'use_chip' in df.columns:
        col_type = 'use_chip'
    elif 'type' not in df.columns:
        return []

    stats = df[col_type].value_counts().reset_index()
    stats.columns = ['type', 'count']
    return stats.to_dict(orient="records")

# --- BONUS : TOP SECTEURS (Celle qui manquait aussi !) ---
def get_top_merchants_categories(limit: int = 5) -> List[Dict[str, Any]]:
    """Top des secteurs d'activité (Basé sur les codes MCC)."""
    df = settings.get_df()
    if df.empty: return []

    # Adaptation à ton fichier : On utilise 'mcc'
    target_col = 'mcc'
    if target_col not in df.columns:
        return [{"error": "Colonne MCC introuvable"}]

    top_mcc = df[target_col].value_counts().head(limit).reset_index()
    top_mcc.columns = ['category_code', 'count']
    return top_mcc.to_dict(orient="records")

# --- ROUTE 10 : HISTOGRAMME ---
def get_amount_distribution() -> Dict[str, List[Any]]:
    """Calcul de l'histogramme des montants."""
    df = settings.get_df()
    if df.empty: return {"bins": [], "counts": []}

    try:
        # Nettoyage des données
        amounts = _clean_amount_column(df)

        # Définition des tranches (Bins)
        bins = [0, 50, 100, 500, 1000, 5000, 999999999]
        labels = ["0-50", "50-100", "100-500", "500-1000", "1000-5000", "5000+"]

        categories = pd.cut(amounts, bins=bins, labels=labels, right=False)
        counts = categories.value_counts().sort_index()
        
        return {
            "bins": counts.index.tolist(),
            "counts": counts.values.tolist()
        }
    except Exception as e:
        print(f"Erreur calcul histogramme: {e}")
        return {"bins": [], "counts": []}

# --- ROUTE 12 : STATS JOURNALIERES ---
def get_daily_stats() -> List[Dict[str, Any]]:
    """Calcul du volume par jour."""
    df = settings.get_df()
    if df.empty: return []

    if 'date' not in df.columns:
        return [{"error": "Pas de colonne date trouvée"}]

    try:
        temp_df = df[['date', 'amount']].copy()
        
        # Nettoyage montant
        temp_df['amount'] = _clean_amount_column(temp_df)
        
        # Conversion Date
        temp_df['date'] = pd.to_datetime(temp_df['date'], errors='coerce')
        
        # Groupement par jour
        daily = temp_df.groupby(temp_df['date'].dt.date).agg(
            transaction_count=('amount', 'count'),
            total_amount=('amount', 'sum')
        ).reset_index()

        # Tri par date récente (30 derniers jours)
        daily = daily.sort_values('date', ascending=False).head(30)
        
        return daily.to_dict(orient="records")
        
    except Exception as e:
        print(f"Erreur stats daily: {e}")
        return []