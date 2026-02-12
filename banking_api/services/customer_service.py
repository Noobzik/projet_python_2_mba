"""Service client pour les opérations liées aux clients.

Ce module gère l’agrégation et l’analyse des profils clients
à partir de l’historique des transactions.
"""
import pandas as pd
from typing import List, Optional
from banking_api.utils.data_loader import DataLoader
from banking_api.models.schemas import (
    CustomerProfile,
    CustomerListResponse,
    TopCustomer
)
from banking_api.config import DEFAULT_PAGE, DEFAULT_LIMIT, DEFAULT_TOP_N


class CustomerService:
    """Classe de service pour les opérations liées aux clients.

    Attributes
    ----------
    data_loader : DataLoader
        Instance du chargeur de données
    """

    def __init__(self) -> None:
        """Initialiser le service client."""
        self.data_loader = DataLoader()

    def get_all_customers(
        self,
        page: int = DEFAULT_PAGE,
        limit: int = DEFAULT_LIMIT
    ) -> CustomerListResponse:
        """Récupérer une liste paginée des clients uniques.

        Parameters
        ----------
        page : int, optional
            Numéro de page, par défaut DEFAULT_PAGE
        limit : int, optional
            Nombre d’éléments par page, par défaut DEFAULT_LIMIT

        Returns
        -------
        CustomerListResponse
            Liste paginée des clients
        """
        df = self.data_loader.get_data()

        unique_customers = pd.concat([
            df['nameOrig'],
            df['nameDest']
        ]).unique().tolist()

        unique_customers = sorted(unique_customers)
        total = len(unique_customers)

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        customers_page = unique_customers[start_idx:end_idx]

        return CustomerListResponse(
            page=page,
            limit=limit,
            total=total,
            customers=customers_page
        )

    def get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """Récupérer le profil client avec résumé des transactions.

        Parameters
        ----------
        customer_id : str
            Identifiant du client

        Returns
        -------
        Optional[CustomerProfile]
            Profil client si trouvé, None sinon
        """
        df = self.data_loader.get_data()

        customer_txns = df[
            (df['nameOrig'] == customer_id)
            | (df['nameDest'] == customer_id)
        ]

        if len(customer_txns) == 0:
            return None

        transactions_count = len(customer_txns)
        avg_amount = float(customer_txns['amount'].mean())
        total_amount = float(customer_txns['amount'].sum())

        fraud_involved = customer_txns['isFraud'].sum() > 0
        fraud_count = int(customer_txns['isFraud'].sum())

        return CustomerProfile(
            id=customer_id,
            transactions_count=transactions_count,
            avg_amount=round(avg_amount, 2),
            total_amount=round(total_amount, 2),
            fraudulent=bool(fraud_involved),
            fraud_count=fraud_count
        )

    def get_top_customers(self, n: int = DEFAULT_TOP_N) -> List[TopCustomer]:
        """Récupérer les N meilleurs clients selon le volume de transactions.

        Parameters
        ----------
        n : int, optional
            Nombre de meilleurs clients à retourner, par défaut DEFAULT_TOP_N

        Returns
        -------
        List[TopCustomer]
            Meilleurs clients selon le volume
        """
        df = self.data_loader.get_data()

        orig_volume = df.groupby('nameOrig').agg({
            'amount': ['sum', 'count']
        }).reset_index()
        orig_volume.columns = ['customer_id', 'total_volume', 'transaction_count']

        dest_volume = df.groupby('nameDest').agg({
            'amount': ['sum', 'count']
        }).reset_index()
        dest_volume.columns = ['customer_id', 'total_volume', 'transaction_count']

        combined = pd.concat([orig_volume, dest_volume])

        aggregated = combined.groupby('customer_id').agg({
            'total_volume': 'sum',
            'transaction_count': 'sum'
        }).reset_index()

        top_customers_df = aggregated.nlargest(n, 'total_volume')

        top_customers = []
        for _, row in top_customers_df.iterrows():
            top_customers.append(TopCustomer(
                customer_id=str(row['customer_id']),
                total_volume=round(float(row['total_volume']), 2),
                transaction_count=int(row['transaction_count'])
            ))

        return top_customers
