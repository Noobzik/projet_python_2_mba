"""
Service de gestion du chargement et accès aux données.

Ce module gère le chargement des datasets CSV et JSON,
et fournit un accès centralisé aux données.
"""

from pathlib import Path
from typing import Optional

import pandas as pd


class DataLoader:
    """
    Gestionnaire de chargement des données.

    Cette classe singleton gère le chargement et la mise en cache
    des datasets de transactions, utilisateurs, cartes et fraudes.

    Attributes
    ----------
    _instance : Optional[DataLoader]
        Instance singleton
    _transactions_df : Optional[pd.DataFrame]
        DataFrame des transactions
    _users_df : Optional[pd.DataFrame]
        DataFrame des utilisateurs
    _cards_df : Optional[pd.DataFrame]
        DataFrame des cartes
    _fraud_labels : Optional[dict]
        Labels de fraude
    _mcc_codes : Optional[dict]
        Codes MCC
    data_path : Path
        Chemin vers le dossier data
    """

    _instance: Optional["DataLoader"] = None
    _transactions_df: Optional[pd.DataFrame] = None
    _users_df: Optional[pd.DataFrame] = None
    _cards_df: Optional[pd.DataFrame] = None
    _fraud_labels: Optional[dict] = None
    _mcc_codes: Optional[dict] = None

    def __new__(cls) -> "DataLoader":
        """
        Crée ou retourne l'instance singleton.

        Returns
        -------
        DataLoader
            Instance unique du DataLoader
        """
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialise le DataLoader."""
        if not hasattr(self, "initialized"):
            import logging
            import os

            logger = logging.getLogger(__name__)

            # Stratégie de résolution du chemin des données :
            # 1. Variable d'environnement BANKING_API_DATA_PATH
            # 2. Dossier 'data' dans le répertoire courant (CWD)
            # 3. Dossier 'data' relatif au package (fallback dev/install)

            env_path = os.environ.get("BANKING_API_DATA_PATH")
            cwd_path = Path.cwd() / "data"
            package_path = Path(__file__).parent.parent.parent / "data"

            if env_path and Path(env_path).exists():
                self.data_path = Path(env_path)
                logger.info(f"Using data path from environment: {self.data_path}")
            elif cwd_path.exists():
                self.data_path = cwd_path
                logger.info(f"Using data path from CWD: {self.data_path}")
            else:
                self.data_path = package_path
                logger.info(f"Using default package data path: {self.data_path}")

            self.initialized = True

    def load_data(self) -> None:
        """
        Charge tous les datasets en mémoire.

        Raises
        ------
        FileNotFoundError
            Si les fichiers de données ne sont pas trouvés
        """
        # Chargement des transactions
        transactions_file: Path = self.data_path / "transactions_data.csv"
        if transactions_file.exists():
            import logging
            logger = logging.getLogger(__name__)

            # Force reading 'amount' column as string to handle $ symbols
            self._transactions_df = pd.read_csv(
                transactions_file,
                dtype={"amount": str}
            )

            # Nettoyer et convertir les types de données
            if "id" in self._transactions_df.columns:
                self._transactions_df["id"] = self._transactions_df["id"].astype(int)

            # Nettoyer la colonne amount - remove $ and convert to float
            if "amount" in self._transactions_df.columns:
                logger.info(f"Original amount sample: {self._transactions_df['amount'].head(5).tolist()}")

                self._transactions_df["amount"] = (
                    self._transactions_df["amount"]
                    .astype(str)
                    .str.replace("$", "", regex=False)
                    .str.replace(",", "", regex=False)  # Remove commas if any
                    .str.strip()
                    .replace(["", "nan", "None"], "0")
                    .astype(float)
                )

                logger.info(f"Converted amount sample: {self._transactions_df['amount'].head(5).tolist()}")
            # Convertir les autres colonnes numériques
            numeric_columns = ["client_id", "card_id", "merchant_id", "mcc"]
            for col in numeric_columns:
                if col in self._transactions_df.columns:
                    self._transactions_df[col] = (
                        pd.to_numeric(self._transactions_df[col], errors="coerce")
                        .fillna(0)
                        .astype(int)
                    )

            # Convertir zip en float (peut contenir des NaN)
            if "zip" in self._transactions_df.columns:
                self._transactions_df["zip"] = pd.to_numeric(
                    self._transactions_df["zip"], errors="coerce"
                )

            # Convertir errors NaN en None pour Pydantic
            if "errors" in self._transactions_df.columns:
                self._transactions_df["errors"] = self._transactions_df[
                    "errors"
                ].replace({pd.NA: None, float("nan"): None})
                # Convertir les NaN en None
                self._transactions_df["errors"] = self._transactions_df["errors"].where(
                    self._transactions_df["errors"].notna(), None
                )

            # Convertir les NaN en string vide pour les colonnes de texte
            string_columns = ["use_chip", "merchant_city", "merchant_state"]
            for col in string_columns:
                if col in self._transactions_df.columns:
                    self._transactions_df[col] = self._transactions_df[col].fillna(
                        "UNKNOWN"
                    )
        else:
            raise FileNotFoundError(
                f"Fichier transactions non trouvé: {transactions_file}"
            )

        # Chargement des utilisateurs
        users_file: Path = self.data_path / "users_data.csv"
        if users_file.exists():
            self._users_df = pd.read_csv(users_file)

        # Chargement des cartes
        cards_file: Path = self.data_path / "cards_data.csv"
        if cards_file.exists():
            self._cards_df = pd.read_csv(cards_file)

        # Chargement des labels de fraude
        fraud_file: Path = self.data_path / "train_fraud_labels.json"
        if fraud_file.exists():
            import json

            with open(fraud_file, "r") as f:
                self._fraud_labels = json.load(f)

        # Chargement des codes MCC
        mcc_file: Path = self.data_path / "mcc_codes.json"
        if mcc_file.exists():
            import json

            with open(mcc_file, "r") as f:
                self._mcc_codes = json.load(f)

    def get_transactions(self) -> pd.DataFrame:
        """
        Retourne le DataFrame des transactions.

        Returns
        -------
        pd.DataFrame
            DataFrame des transactions

        Raises
        ------
        ValueError
            Si les données n'ont pas été chargées
        """
        if self._transactions_df is None:
            self.load_data()
        if self._transactions_df is None:
            raise ValueError("Les données de transactions ne sont pas chargées")
        return self._transactions_df

    def get_users(self) -> Optional[pd.DataFrame]:
        """
        Retourne le DataFrame des utilisateurs.

        Returns
        -------
        Optional[pd.DataFrame]
            DataFrame des utilisateurs ou None
        """
        return self._users_df

    def get_cards(self) -> Optional[pd.DataFrame]:
        """
        Retourne le DataFrame des cartes.

        Returns
        -------
        Optional[pd.DataFrame]
            DataFrame des cartes ou None
        """
        return self._cards_df

    def get_fraud_labels(self) -> Optional[dict]:
        """
        Retourne les labels de fraude.

        Returns
        -------
        Optional[dict]
            Dictionnaire des labels de fraude ou None
        """
        return self._fraud_labels

    def get_mcc_codes(self) -> Optional[dict]:
        """
        Retourne les codes MCC.

        Returns
        -------
        Optional[dict]
            Dictionnaire des codes MCC ou None
        """
        return self._mcc_codes

    def is_loaded(self) -> bool:
        """
        Vérifie si les données sont chargées.

        Returns
        -------
        bool
            True si les données sont chargées, False sinon
        """
        return self._transactions_df is not None


# Instance globale
data_loader: DataLoader = DataLoader()
