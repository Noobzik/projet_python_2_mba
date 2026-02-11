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
            fraud_labels_path = str(
                base_dir / "data" / "train_fraud_labels.json"
            )
        else:
            fraud_labels_path = None

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Dataset not found at {file_path}. "
                "Please download from Kaggle and place in data/ directory."
            )

        # Check for cached pickle file
        pickle_path = file_path.replace('.csv', '.pkl')

        if os.path.exists(pickle_path):
            csv_mtime = os.path.getmtime(file_path)
            pkl_mtime = os.path.getmtime(pickle_path)

            if pkl_mtime > csv_mtime:
                print(f"Loading data from cache: {pickle_path}")
                try:
                    self._data = pd.read_pickle(pickle_path)

                    # Ensure consistency if fraud file changed (simplified check)
                    # For strict correctness, we should also reject cache if
                    # fraud file is newer. But assuming fraud labels are static.
                    return self._data
                except Exception as e:
                    print(f"Failed to load cache: {e}. Reloading from CSV.")

        print(f"Loading data from CSV: {file_path}")

        # Load transactions with efficient date parsing
        # Try to use pyarrow engine if available, otherwise default
        try:
            self._data = pd.read_csv(
                file_path,
                parse_dates=['date'],
                # Hint for faster parsing if format is consistent
                date_format='%Y-%m-%d %H:%M:%S'
            )
        except (ValueError, TypeError):
            # Fallback if date_format doesn't match or other issue
            self._data = pd.read_csv(file_path, parse_dates=['date'])

        # Convert id to string for consistency
        self._data['id'] = self._data['id'].astype(str)

        # Parse amount column if it's a string
        if 'amount' in self._data.columns and \
                self._data['amount'].dtype == 'object':
            # Use string slicing which is faster than replace for fixed formats
            # like $XX.XX. Assuming format is always $...
            try:
                # Vectorized slice and convert
                self._data['amount'] = (
                    self._data['amount'].str.slice(1).astype(float)
                )
            except ValueError:
                # Fallback to slower replace if dirty data
                self._data['amount'] = (
                    self._data['amount']
                    .str.replace('$', '', regex=False)
                    .str.replace(',', '', regex=False)
                    .astype(float)
                )

        # Clean NaN values to prevent JSON serialization errors
        # Replace NaN in numeric columns with 0 or appropriate defaults
        numeric_columns = self._data.select_dtypes(
            include=['float64', 'int64']
        ).columns
        for col in numeric_columns:
            if col == 'zip':
                # Keep zip as nullable, will be handled in model
                continue
            self._data[col] = self._data[col].fillna(0)

        # Replace NaN in string columns with None or empty string
        string_columns = self._data.select_dtypes(include=['object']).columns

        for col in string_columns:
            self._data[col] = self._data[col].fillna('')

        # Optimize types for low cardinality columns
        # 'use_chip' has only 3 values. Validated via unique()
        if 'use_chip' in self._data.columns:
            self._data['use_chip'] = self._data['use_chip'].astype('category')

        # 'merchant_state' has limited number of states
        if 'merchant_state' in self._data.columns:
            self._data['merchant_state'] = (
                self._data['merchant_state'].astype('category')
            )

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
            self._data['isFraud'] = (
                self._data['id'].map(fraud_dict).fillna(0).astype('int8')
            )
        else:
            # Default to 0 if fraud labels not found
            if 'isFraud' not in self._data.columns:
                self._data['isFraud'] = 0
            else:
                self._data['isFraud'] = (
                    self._data['isFraud'].fillna(0).astype('int8')
                )

        # Sort by date once to optimize time-based queries
        # This makes getting recent transactions O(1) instead of O(N log N)
        if 'date' in self._data.columns:
            self._data.sort_values('date', inplace=True)

        print(f"Saving data to cache: {pickle_path}")
        try:
            self._data.to_pickle(pickle_path)
        except Exception as e:
            print(f"Failed to save cache: {e}")

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
