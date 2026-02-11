"""Customer service layer.

This module provides business logic for customer-related operations.
"""

from typing import List
import pandas as pd
from ..models.customer import CustomerProfile, CustomerList, TopCustomer
from ..utils.data_loader import DataLoader


class CustomerService:
    """Service for customer-related operations.

    This service handles customer profile and transaction analysis.
    """

    def __init__(self) -> None:
        """Initialize the customer service."""
        self.data_loader = DataLoader()

    def get_customers(self, page: int = 1, limit: int = 50) -> CustomerList:
        """Get paginated list of unique customers.

        Parameters
        ----------
        page : int
            Page number (1-indexed).
        limit : int
            Number of items per page.

        Returns
        -------
        CustomerList
            Paginated list of customer IDs.
        """
        df = self.data_loader.get_data()
        unique_customers = sorted(df['client_id'].unique().tolist())

        total = len(unique_customers)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        customers = unique_customers[start_idx:end_idx]

        return CustomerList(
            page=page,
            limit=limit,
            total=total,
            customers=customers
        )

    def get_customer_profile(self, customer_id: int) -> CustomerProfile:
        """Get customer profile with transaction summary.

        Parameters
        ----------
        customer_id : int
            Customer identifier.

        Returns
        -------
        CustomerProfile
            Customer profile with statistics.

        Raises
        ------
        ValueError
            If customer is not found.
        """
        df = self.data_loader.get_data()

        # Filter for customer first to reduce data size
        customer_df = df[df['client_id'] == customer_id]

        if customer_df.empty:
            raise ValueError(f"Customer {customer_id} not found")

        # Parse amount if needed
        if customer_df['amount'].dtype == 'object':
            amounts = (
                customer_df['amount']
                .str.replace('$', '')
                .str.replace(',', '')
                .astype(float)
            )
        else:
            amounts = customer_df['amount']

        transactions_count = len(customer_df)
        avg_amount = float(amounts.mean())
        total_amount = float(amounts.sum())
        fraud_count = int(customer_df['isFraud'].sum())
        fraudulent = fraud_count > 0

        # Handle NaN values
        if pd.isna(avg_amount):
            avg_amount = 0.0
        if pd.isna(total_amount):
            total_amount = 0.0

        return CustomerProfile(
            id=customer_id,
            transactions_count=transactions_count,
            avg_amount=avg_amount,
            total_amount=total_amount,
            fraudulent=fraudulent,
            fraud_count=fraud_count
        )

    def get_top_customers(self, n: int = 10) -> List[TopCustomer]:
        """Get top customers by transaction volume.

        Parameters
        ----------
        n : int
            Number of top customers to retrieve.

        Returns
        -------
        List[TopCustomer]
            List of top customers sorted by total amount.
        """
        df = self.data_loader.get_data()

        # Parse amount if needed
        if df['amount'].dtype == 'object':
            df = df.copy()
            df['amount'] = (
                df['amount']
                .str.replace('$', '')
                .str.replace(',', '')
                .astype(float)
            )

        customer_totals = df.groupby('client_id').agg({
            'amount': ['sum', 'count']
        }).reset_index()

        customer_totals.columns = pd.Index(['id', 'total_amount', 'transactions_count'])
        customer_totals = customer_totals.sort_values(
            'total_amount',
            ascending=False
        ).head(n)

        result = []
        for _, row in customer_totals.iterrows():
            total_amount = row['total_amount']
            if pd.isna(total_amount):
                total_amount = 0.0

            result.append(TopCustomer(
                id=str(row['id']),
                total_amount=float(total_amount),
                transactions_count=int(row['transactions_count'])
            ))

        return result
