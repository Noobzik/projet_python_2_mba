import os
import pandas as pd
import kagglehub
import json
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PrivateAttr

class Settings(BaseSettings):
    # Infos Projet
    PROJECT_NAME: str = "Banking Transactions API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    START_TIME: datetime = Field(default_factory=datetime.now)

    # --- 2. Cache Mémoire (PrivateAttr pour éviter la validation Pydantic) ---
    # On utilise PrivateAttr pour dire à Pydantic : "Touche pas à ça, c'est interne"
    _df: Any = PrivateAttr(default=None)
    _users: Any = PrivateAttr(default=None)
    _cards: Any = PrivateAttr(default=None)
    _mcc: Any = PrivateAttr(default=None)

    # --- CONFIGURATION PYDANTIC V2 (Le fix des warnings) ---
    model_config = SettingsConfigDict(
        case_sensitive=True,
        arbitrary_types_allowed=True, # Autorise les objets complexes comme DataFrame
        env_file=".env",
        extra="ignore"
    )

    # --- 3. Accesseurs (Getters) ---
    def get_df(self) -> pd.DataFrame:
        if self._df is None:
            self._load_data()
        return self._df

    def get_users(self) -> pd.DataFrame:
        if self._users is None:
            self._load_data()
        return self._users

    def get_cards(self) -> pd.DataFrame:
        if self._cards is None:
            self._load_data()
        return self._cards

    def get_mcc(self) -> Dict[str, str]:
        if self._mcc is None:
            self._load_data()
        return self._mcc

    # --- 4. Logique de Chargement (KaggleHub) ---
    def _load_data(self):
        print("Synchronisation avec KaggleHub...")
        try:
            # Téléchargement automatique (Cache système)
            path = kagglehub.dataset_download("computingvictor/transactions-fraud-datasets")
            print(f"Dataset disponible dans : {path}")

            # Définition des chemins
            tx_path = os.path.join(path, "transactions_data.csv")
            users_path = os.path.join(path, "users_data.csv")
            cards_path = os.path.join(path, "cards_data.csv")
            fraud_path = os.path.join(path, "train_fraud_labels.json")
            mcc_path = os.path.join(path, "mcc_codes.json")

            # A. Chargement Transactions
            print("Chargement des Transactions (1/5)...")
            self._df = pd.read_csv(tx_path, low_memory=False)
            self._df.columns = self._df.columns.str.strip()

            # Nettoyage des montants ($)
            if self._df['amount'].dtype == object:
                 self._df['amount'] = self._df['amount'].astype(str).str.replace(r'[\$,()]', '', regex=True).astype(float)

            # B. Chargement Fraude & Fusion
            print("Chargement des Labels Fraude (2/5)...")
            with open(fraud_path, 'r') as f:
                data = json.load(f)
            
            fraud_df = pd.DataFrame.from_dict(data['target'], orient='index', columns=['fraud_label'])
            fraud_df.index.name = 'id'
            fraud_df.index = fraud_df.index.astype(int)

            print("Fusion Transactions + Fraude...")
            self._df = self._df.merge(fraud_df, on='id', how='left')
            self._df['isFraud'] = self._df['fraud_label'].apply(lambda x: 1 if x == 'Yes' else 0)
            
            if 'use_chip' in self._df.columns:
                self._df['type'] = self._df['use_chip']

            # C. Autres fichiers
            print("Chargement des Users (3/5)...")
            self._users = pd.read_csv(users_path)
            if 'yearly_income' in self._users.columns and self._users['yearly_income'].dtype == object:
                 self._users['yearly_income'] = self._users['yearly_income'].str.replace(r'[\$,]', '', regex=True).astype(float)

            print("Chargement des Cartes (4/5)...")
            self._cards = pd.read_csv(cards_path)

            print("Chargement des Codes MCC (5/5)...")
            try:
                with open(mcc_path, 'r') as f:
                    self._mcc = json.load(f)
            except Exception:
                self._mcc = {}

            print(f"✅ TOUT EST PRÊT ! {len(self._df)} transactions chargées.")

        except Exception as e:
            print(f"❌ ERREUR CHARGEMENT DONNÉES : {e}")
            # Fallback pour ne pas faire crasher l'API si Kaggle échoue
            self._df = pd.DataFrame(columns=['id', 'amount', 'type', 'isFraud'])
            self._users = pd.DataFrame()
            self._cards = pd.DataFrame()
            self._mcc = {}

# Instanciation unique
settings = Settings()