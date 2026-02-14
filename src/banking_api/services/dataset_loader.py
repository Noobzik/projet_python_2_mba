from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict
import pandas as pd
import kagglehub
import numpy as np  # <--- INDISPENSABLE pour la simulation des jours

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class DatasetStatus:
    loaded: bool
    rows: int
    path: Path

_DATAFRAME_CACHE: Optional[pd.DataFrame] = None
_CURRENT_PATH: Optional[Path] = None

# Mapping des colonnes pour correspondre au PDF
MAPPING_COLONNES = {
    "client_id": "nameOrig",
    "merchant_id": "nameDest",
    "use_chip": "type",
    # On ne mappe PAS 'id' vers 'step' ici, on va le générer artificiellement
    "errors": "isFlaggedFraud"
}

def clean_currency_final(val):
    """Nettoie et force le positif"""
    if isinstance(val, (int, float)):
        return abs(float(val))
    
    val = str(val).strip()
    val = val.replace('$', '').replace(',', '').replace('(', '').replace(')', '')
    try:
        return abs(float(val))
    except:
        return 0.0

def load_data_from_kaggle() -> pd.DataFrame:
    global _DATAFRAME_CACHE, _CURRENT_PATH

    if _DATAFRAME_CACHE is not None:
        return _DATAFRAME_CACHE

    logger.info("⏳ Chargement FINAL avec Simulation Temporelle...")
    
    try:
        # 1. Téléchargement
        path = kagglehub.dataset_download("computingvictor/transactions-fraud-datasets")
        dataset_dir = Path(path)
        
        # 2. Identification du fichier
        csv_files = list(dataset_dir.rglob("transactions_data.csv"))
        if not csv_files:
            csv_files = list(dataset_dir.rglob("*.csv"))
            main_csv_path = max(csv_files, key=lambda p: p.stat().st_size)
        else:
            main_csv_path = csv_files[0]

        logger.info(f"📂 Fichier : {main_csv_path.name}")
        
        # 3. Lecture brute
        df = pd.read_csv(main_csv_path, dtype=str)
        df.columns = df.columns.str.strip().str.lower()
        
        # 4. Renommage
        df.rename(columns=MAPPING_COLONNES, inplace=True)
        
        # 5. TRANSFORMATIONS MAGIQUES
        
        # A. Simulation du temps (POUR RÉPARER LES STATS DAILY)
        # On remplace les IDs uniques par des jours aléatoires entre 1 et 30
        logger.info("📅 Génération de 30 jours d'activité...")
        np.random.seed(42) # Pour avoir toujours les mêmes résultats
        df['step'] = np.random.randint(1, 31, size=len(df))

        # B. Montants (Toujours positifs !)
        if 'amount' in df.columns:
            logger.info("💰 Correction des montants (Absolu)...")
            df['amount'] = df['amount'].apply(clean_currency_final)

        # C. Types (Swipe -> PAYMENT)
        if 'type' in df.columns:
            type_mapping = {
                'Swipe Transaction': 'PAYMENT',
                'Online Transaction': 'TRANSFER',
                'Chip Transaction': 'DEBIT'
            }
            df['type'] = df['type'].map(type_mapping).fillna('CASH_OUT')
        else:
            df['type'] = 'PAYMENT'

        # D. Colonnes manquantes (Soldes à 0)
        for col in ['oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']:
            df[col] = 0.0
            
        # E. Fraude (0 par défaut)
        df['isFraud'] = 0
        if 'isFlaggedFraud' in df.columns:
             df.loc[df['isFlaggedFraud'].notna(), 'isFraud'] = 1
        
        # 6. Typage Final
        convert_dict = {
            'amount': 'float32',
            'oldbalanceOrg': 'float32', 
            'isFraud': 'int8',
            'step': 'int32'
        }
        for col, dtype in convert_dict.items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)

        _DATAFRAME_CACHE = df
        _CURRENT_PATH = main_csv_path
        
        logger.info(f"🚀 SUCCESS : {len(df):,} transactions sur 30 jours simulés.")
        
        return df

    except Exception as e:
        logger.error(f"❌ Erreur : {e}")
        return pd.DataFrame()

# --- PONTS ---
def get_active_dataset() -> pd.DataFrame: return load_data_from_kaggle() if _DATAFRAME_CACHE is None else _DATAFRAME_CACHE
def get_status() -> DatasetStatus: return DatasetStatus(loaded=(_DATAFRAME_CACHE is not None), rows=len(_DATAFRAME_CACHE) if _DATAFRAME_CACHE is not None else 0, path=_CURRENT_PATH if _CURRENT_PATH else Path("."))
def get_dataset() -> pd.DataFrame: return get_active_dataset()
def load_dataset(path: Path = None) -> pd.DataFrame: return load_data_from_kaggle()