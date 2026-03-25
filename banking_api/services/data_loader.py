"""
Data Loader Service.

Provides a singleton that loads the CSV dataset once and exposes
a cleaned ``pandas.DataFrame`` to all services.

Notes
-----
The CSV file path is resolved via the ``BANKING_CSV_PATH`` environment
variable (defaults to ``data/transactions_data.csv`` relative to the
current working directory).
"""

import os
import pandas as pd
from pathlib import Path


class DataLoader:
    """Singleton wrapper around the transactions CSV dataset.

    Parameters
    ----------
    csv_path : str, optional
        Absolute or relative path to the CSV file.  When *None* the value
        of the ``BANKING_CSV_PATH`` environment variable is used, falling
        back to ``data/transactions_data.csv``.

    Attributes
    ----------
    _instance : DataLoader or None
        Class-level reference to the unique instance.
    _df : pd.DataFrame
        The loaded dataset.
    _deleted_ids : set[str]
        Transaction IDs that have been soft-deleted via the DELETE endpoint.
    """

    _instance: "DataLoader | None" = None
    _df: pd.DataFrame = pd.DataFrame()
    _deleted_ids: set[str] = set()

    def __init__(self, csv_path: str | None = None) -> None:
        path: str = csv_path or os.environ.get(
            "BANKING_CSV_PATH", "data/transactions_data.csv"
        )
        if Path(path).exists():
            df: pd.DataFrame = pd.read_csv(path)
            df["id"] = "tx_" + df.index.astype(str).str.zfill(7)
            self._df = df
        else:
            # Build an empty DataFrame with the expected schema so that
            # the application can start without the dataset (useful for
            # CI and unit tests that inject their own fixture data).
            self._df = pd.DataFrame(
                columns=[
                    "id", "step", "type", "amount", "nameOrig",
                    "oldbalanceOrg", "newbalanceOrig", "nameDest",
                    "oldbalanceDest", "newbalanceDest", "isFraud",
                    "isFlaggedFraud",
                ]
            )

    @classmethod
    def get_instance(cls) -> "DataLoader":
        """Return (and lazily create) the singleton instance.

        Returns
        -------
        DataLoader
            The unique application-wide data loader.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Destroy the singleton (useful in test teardown)."""
        cls._instance = None
        cls._deleted_ids = set()

    @property
    def df(self) -> pd.DataFrame:
        """Active (non-deleted) rows of the dataset.

        Returns
        -------
        pd.DataFrame
            DataFrame excluding soft-deleted transaction IDs.
        """
        if self._deleted_ids:
            return self._df[~self._df["id"].isin(self._deleted_ids)]
        return self._df

    def soft_delete(self, transaction_id: str) -> bool:
        """Mark a transaction as deleted.

        Parameters
        ----------
        transaction_id : str
            The ``id`` field of the transaction to remove.

        Returns
        -------
        bool
            *True* if the ID existed and was deleted, *False* otherwise.
        """
        if transaction_id in self._df["id"].values:
            self._deleted_ids.add(transaction_id)
            return True
        return False

    @property
    def is_loaded(self) -> bool:
        """Return whether the dataset contains at least one row."""
        return len(self._df) > 0
