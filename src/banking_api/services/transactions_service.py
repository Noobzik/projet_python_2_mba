"""Transaction service layer.

This module provides business logic for transaction operations.
"""

from typing import List, Optional, Any, Dict
import pandas as pd
from ..models.transaction import Transaction, TransactionList, TransactionSearch
from ..utils.data_loader import DataLoader


class TransactionsService:
    """Service for transaction-related operations.

    This service handles transaction retrieval, filtering, and searching.
    """

    def __init__(self) -> None:
        """Initialize the transactions service."""
        self.data_loader = DataLoader()

    def get_transactions(
        self,
        page: int = 1,
        limit: int = 50,
        use_chip_filter: Optional[str] = None,
        is_fraud: Optional[int] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        merchant_state: Optional[str] = None
    ) -> TransactionList:
        """Get paginated list of transactions with filters.

        Parameters
        ----------
        page : int
            Page number (1-indexed).
        limit : int
            Number of items per page.
        use_chip_filter : Optional[str]
            Filter by transaction method.
        is_fraud : Optional[int]
            Filter by fraud status (0 or 1).
        min_amount : Optional[float]
            Minimum transaction amount.
        max_amount : Optional[float]
            Maximum transaction amount.
        merchant_state : Optional[str]
            Filter by merchant state.

        Returns
        -------
        TransactionList
            Paginated list of transactions.
        """
        df = self.data_loader.get_data()

        # Apply filters - Numeric/Boolean first for performance
        if is_fraud is not None:
            df = df[df['isFraud'] == is_fraud]

        if min_amount is not None:
            df = df[df['amount'] >= min_amount]

        if max_amount is not None:
            df = df[df['amount'] <= max_amount]

        # Categorical/String filters
        if use_chip_filter:
            # use_chip is categorical, str accessor works but we can optimize
            # if exact match. For now stick to contains as per feature spec,
            # it's reasonably fast on categories
            mask = df['use_chip'].str.contains(
                use_chip_filter, case=False, na=False
            )
            df = df[mask]

        if merchant_state:
            df = df[df['merchant_state'] == merchant_state]

        total = len(df)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        transactions_df = df.iloc[start_idx:end_idx]

        # Optimize iteration by using to_dict('records')
        # We need to clean the rows (handle NaN) similar to what _clean_row did,
        # but _clean_row was doing it row by row.
        # Since we cleaned NaNs in DataLoader, we might be able to use to_dict
        # directy provided the keys match.

        records = transactions_df.to_dict('records')
        transactions = []
        for row in records:
            # Ensure we don't return NaNs if any slipped through
            # or if new columns added
            clean_row: Dict[str, Any] = {
                str(k): (None if pd.isna(v) else v) for k, v in row.items()
            }
            # key "isFraud" needs to be int if present, ensuring type safety
            if 'isFraud' in clean_row and clean_row['isFraud'] is not None:
                clean_row['isFraud'] = int(clean_row['isFraud'])
            
            transactions.append(Transaction(**clean_row))

        return TransactionList(
            page=page,
            limit=limit,
            total=total,
            transactions=transactions
        )

    def get_transaction_by_id(
        self,
        transaction_id: str
    ) -> Optional[Transaction]:
        """Get a transaction by its ID.

        Parameters
        ----------
        transaction_id : str
            Transaction identifier.

        Returns
        -------
        Optional[Transaction]
            Transaction object if found, None otherwise.
        """
        df = self.data_loader.get_data()
        transaction_df = df[df['id'] == transaction_id]

        if transaction_df.empty:
            return None

        return Transaction(**self._clean_row(transaction_df.iloc[0]))

    def search_transactions(
        self,
        criteria: TransactionSearch,
        page: int = 1,
        limit: int = 50
    ) -> TransactionList:
        """Search transactions with multiple criteria.

        Parameters
        ----------
        criteria : TransactionSearch
            Search criteria.
        page : int
            Page number (1-indexed).
        limit : int
            Number of items per page.

        Returns
        -------
        TransactionList
            Paginated list of matching transactions.
        """
        df = self.data_loader.get_data()

        if criteria.use_chip:
            mask = df['use_chip'].str.contains(
                criteria.use_chip,
                case=False,
                na=False
            )
            df = df[mask]
        if criteria.isFraud is not None:
            df = df[df['isFraud'] == criteria.isFraud]
        if criteria.amount_range:
            df = df[
                (df['amount'] >= criteria.amount_range[0]) &
                (df['amount'] <= criteria.amount_range[1])
            ]
        if criteria.client_id:
            df = df[df['client_id'] == criteria.client_id]
        if criteria.merchant_state:
            df = df[df['merchant_state'] == criteria.merchant_state]
        if criteria.merchant_city:
            df = df[df['merchant_city'] == criteria.merchant_city]

        total = len(df)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        transactions_df = df.iloc[start_idx:end_idx]

        records = transactions_df.to_dict('records')
        transactions = []
        for row in records:
            clean_row: Dict[str, Any] = {
                str(k): (None if pd.isna(v) else v) for k, v in row.items()
            }
            if 'isFraud' in clean_row and clean_row['isFraud'] is not None:
                clean_row['isFraud'] = int(clean_row['isFraud'])
            transactions.append(Transaction(**clean_row))

        return TransactionList(
            page=page,
            limit=limit,
            total=total,
            transactions=transactions
        )

    def get_transaction_methods(self) -> List[str]:
        """Get list of unique transaction methods.

        Returns
        -------
        List[str]
            List of transaction methods.
        """
        df = self.data_loader.get_data()
        return sorted(df['use_chip'].unique().tolist())

    def get_recent_transactions(self, n: int = 10) -> List[Transaction]:
        """Get N most recent transactions.

        Parameters
        ----------
        n : int
            Number of recent transactions to retrieve.

        Returns
        -------
        List[Transaction]
            List of recent transactions.
        """
        df = self.data_loader.get_data()

        # Optimized: O(1) assuming DF is sorted by date in DataLoader (ascending)
        # Take the last n rows and reverse them to show most recent first
        if len(df) >= n:
            recent_df = df.iloc[-n:][::-1]
        else:
            recent_df = df.iloc[::-1]

        records = recent_df.to_dict('records')
        transactions = []
        for row in records:
            clean_row: Dict[str, Any] = {
                str(k): (None if pd.isna(v) else v) for k, v in row.items()
            }
            if 'isFraud' in clean_row and clean_row['isFraud'] is not None:
                clean_row['isFraud'] = int(clean_row['isFraud'])
            transactions.append(Transaction(**clean_row))

        return transactions

    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction (test mode only).

        Parameters
        ----------
        transaction_id : str
            Transaction identifier.

        Returns
        -------
        bool
            True if deleted, False if not found.

        Notes
        -----
        This is a simulated operation for testing purposes.
        In production, this would interact with a database.
        """
        df = self.data_loader.get_data()
        if transaction_id in df['id'].values:
            return True
        return False

    def get_transactions_by_client(
        self,
        client_id: int,
        page: int = 1,
        limit: int = 50
    ) -> TransactionList:
        """Get paginated transactions for a specific client.

        Parameters
        ----------
        client_id : int
            Client identifier.
        page : int
            Page number (1-indexed).
        limit : int
            Number of items per page.

        Returns
        -------
        TransactionList
            Paginated list of transactions for this client.
        """
        df = self.data_loader.get_data()
        filtered_df = df[df['client_id'] == client_id]

        total = len(filtered_df)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        transactions_df = filtered_df.iloc[start_idx:end_idx]
        transactions = [
            Transaction(**self._clean_row(row))
            for _, row in transactions_df.iterrows()
        ]

        return TransactionList(
            page=page,
            limit=limit,
            total=total,
            transactions=transactions
        )

    def get_transactions_to_merchant(
        self,
        merchant_id: int
    ) -> List[Transaction]:
        """Get transactions received by a merchant.

        This method is used by the to-customer route to show transactions
        where a merchant received payments (since the dataset only has
        customer-to-merchant transactions, not customer-to-customer transfers).

        Parameters
        ----------
        merchant_id : int
            Merchant identifier (passed as customer_id in the route).

        Returns
        -------
        List[Transaction]
            List of transactions received by this merchant.
        """
        df = self.data_loader.get_data()
        filtered_df = df[df['merchant_id'] == merchant_id]

        return [
            Transaction(**self._clean_row(row))
            for _, row in filtered_df.iterrows()
        ]

    def _clean_row(self, row: pd.Series) -> Dict[str, Any]:
        """Clean a row for JSON serialization.

        Parameters
        ----------
        row : pd.Series
            DataFrame row.

        Returns
        -------
        dict
            Cleaned dictionary safe for JSON.
        """
        data = row.to_dict()
        clean_data: Dict[str, Any] = {}
        for key, value in data.items():
            if pd.isna(value):
                clean_data[str(key)] = None
            else:
                clean_data[str(key)] = value
        
        if 'isFraud' in clean_data and clean_data['isFraud'] is not None:
            clean_data['isFraud'] = int(clean_data['isFraud'])
            
        return clean_data
