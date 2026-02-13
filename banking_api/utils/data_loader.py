"""Utilitaires de chargement des données pour le dataset de transactions.

Ce module gère le chargement et le prétraitement du fichier CSV des transactions.
ADAPTÉ pour le dataset des transactions par carte.
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from banking_api.config import DATA_FILE


class DataLoader:
    """Classe singleton pour charger et mettre en cache les données de transactions.

    Cette classe garantit que le dataset est chargé une seule fois et
    fournit un accès aux données pendant tout le cycle de vie de l’application.

    Attributes
    ----------
    _instance : Optional[DataLoader]
        Instance singleton
    _data : Optional[pd.DataFrame]
        Données de transactions mises en cache
    """

    _instance: Optional["DataLoader"] = None
    _data: Optional[pd.DataFrame] = None

    def __new__(cls) -> "DataLoader":
        """Créer l’instance singleton.

        Returns
        -------
        DataLoader
            Instance unique de DataLoader
        """
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance

    def load_data(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """Charger les données de transactions depuis un fichier CSV.

        Parameters
        ----------
        file_path : Optional[Path], optional
            Chemin vers le fichier CSV, par défaut None (utilise la config)

        Returns
        -------
        pd.DataFrame
            Données de transactions chargées

        Raises
        ------
        FileNotFoundError
            Si le fichier CSV n’existe pas
        ValueError
            Si le fichier CSV est vide ou invalide
        """
        if self._data is not None:
            return self._data

        path = file_path if file_path is not None else DATA_FILE

        if not path.exists():
            raise FileNotFoundError(
                f"Fichier de données des transactions introuvable : {path}. "
                "Télécharge-le depuis Kaggle et place-le dans le dossier data/."
            )

        try:
            self._data = pd.read_csv(path)
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement du fichier CSV : {e}")

        if self._data.empty:
            raise ValueError("Les données chargées sont vides")

        required_columns = [
            "id",
            "date",
            "client_id",
            "card_id",
            "amount",
            "use_chip",
            "merchant_id",
            "merchant_city",
            "merchant_state",
            "zip",
            "mcc",
            "errors",
        ]

        missing_cols = set(required_columns) - set(self._data.columns)
        if missing_cols:
            raise ValueError(f"Colonnes obligatoires manquantes : {missing_cols}")

        self._adapt_columns(self._data)

        return self._data

    def _adapt_columns(self, df: pd.DataFrame) -> None:
        """Adapter les colonnes du dataset pour correspondre au schéma attendu.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame à adapter
        """
        df["step"] = df["id"]

        def map_transaction_type(use_chip: str) -> str:
            use_chip_str = str(use_chip)
            if "Chip" in use_chip_str:
                return "PAYMENT"
            elif "Swipe" in use_chip_str:
                return "CASH_OUT"
            elif "Online" in use_chip_str:
                return "TRANSFER"
            else:
                return "DEBIT"

        df["type"] = df["use_chip"].apply(map_transaction_type)

        df["nameOrig"] = "C" + df["client_id"].astype(str).str.zfill(3)

        df["nameDest"] = "M" + df["merchant_id"].astype(str).str.zfill(3)

        amount_clean = (
            df["amount"]
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df["amount"] = amount_clean.astype(float).abs()

        df["isFraud"] = df["errors"].notna().astype(int)

        df["isFlaggedFraud"] = 0

        df["oldbalanceOrg"] = df["amount"] * 10
        df["newbalanceOrig"] = df["oldbalanceOrg"] - df["amount"]
        df["oldbalanceDest"] = df["amount"] * 5
        df["newbalanceDest"] = df["oldbalanceDest"] + df["amount"]

    def get_data(self) -> pd.DataFrame:
        """Récupérer les données de transactions mises en cache.

        Returns
        -------
        pd.DataFrame
            Données de transactions

        Raises
        ------
        RuntimeError
            Si les données n’ont pas encore été chargées
        """
        if self._data is None:
            return self.load_data()
        return self._data

    def reload_data(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """Recharger les données depuis le fichier.

        Parameters
        ----------
        file_path : Optional[Path], optional
            Chemin vers le fichier CSV, par défaut None

        Returns
        -------
        pd.DataFrame
            Données de transactions rechargées
        """
        self._data = None
        return self.load_data(file_path)

    @property
    def is_loaded(self) -> bool:
        """Vérifier si les données sont chargées.

        Returns
        -------
        bool
            True si les données sont chargées, sinon False
        """
        return self._data is not None

    @property
    def record_count(self) -> int:
        """Récupérer le nombre d’enregistrements du dataset.

        Returns
        -------
        int
            Nombre d’enregistrements
        """
        if self._data is None:
            return 0
        return len(self._data)
