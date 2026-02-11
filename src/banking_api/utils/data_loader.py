"""Data loading utilities.

This module handles loading and caching of the transactions dataset.
"""

import os
from typing import Optional
import pandas as pd
from pathlib import Path


class DataLoader:
    """Singleton class for loading and caching transaction data.

    This class ensures the dataset is loaded only once and cached
    in memory for efficient access.

    Attributes
    ----------
    _instance : Optional[DataLoader]
        Singleton instance.
    _data : Optional[pd.DataFrame]
        Cached DataFrame.
    """

    _instance: Optional['DataLoader'] = None
    _data: Optional[pd.DataFrame] = None

    def __new__(cls) -> 'DataLoader':
        """Create or return singleton instance.

        Returns
        -------
        DataLoader
            Singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """Load transaction data from CSV file and merge with fraud labels.

        Parameters
        ----------
        file_path : Optional[str]
            Path to CSV file. If None, uses default location.

        Returns
        -------
        pd.DataFrame
            Loaded transaction data with fraud labels.

        Raises
        ------
        FileNotFoundError
            If the CSV file is not found.
        """
        if self._data is not None:
            return self._data

        if file_path is None:
            base_dir = Path(__file__).parent.parent.parent.parent
            file_path = str(base_dir / "data" / "transactions_data.csv")
            fraud_labels_path = str(base_dir / "data" / "train_fraud_labels.json")
        else:
            fraud_labels_path = None

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Dataset not found at {file_path}. "
                "Please download from Kaggle and place in data/ directory."
            )

        # Load transactions
        self._data = pd.read_csv(file_path)

        # Convert id to string for consistency
        self._data['id'] = self._data['id'].astype(str)

        # Clean NaN values to prevent JSON serialization errors
        # Replace NaN in numeric columns with 0 or appropriate defaults
        numeric_columns = self._data.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            if col == 'zip':
                # Keep zip as nullable, will be handled in model
                continue
            self._data[col] = self._data[col].fillna(0)

        # Replace NaN in string columns with None or empty string
        string_columns = self._data.select_dtypes(include=['object']).columns
        for col in string_columns:
            self._data[col] = self._data[col].fillna('')

        # Load and merge fraud labels
        if fraud_labels_path and os.path.exists(fraud_labels_path):
            import json
            with open(fraud_labels_path, 'r') as f:
                fraud_data = json.load(f)

            # Map fraud labels (Yes -> 1, No -> 0)
            fraud_dict = {
                k: 1 if v == "Yes" else 0
                for k, v in fraud_data.get('target', {}).items()
            }

            # Add isFraud column
            self._data['isFraud'] = self._data['id'].map(fraud_dict).fillna(0).astype(int)
        else:
            # Default to 0 if fraud labels not found
            self._data['isFraud'] = 0

        return self._data

    def get_data(self) -> pd.DataFrame:
        """Get cached transaction data.

        Returns
        -------
        pd.DataFrame
            Cached transaction data.

        Raises
        ------
        RuntimeError
            If data has not been loaded yet.
        """
        if self._data is None:
            raise RuntimeError(
                "Data not loaded. Call load_data() first."
            )
        return self._data

    def is_loaded(self) -> bool:
        """Check if data is loaded.

        Returns
        -------
        bool
            True if data is loaded, False otherwise.
        """
        return self._data is not None

    def clear_cache(self) -> None:
        """Clear cached data.

        This method is primarily for testing purposes.
        """
        self._data = None
