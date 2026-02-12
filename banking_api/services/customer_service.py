"""Service client pour les opérations liées aux clients.

Ce module gère l'agrégation et l'analyse des profils clients
à partir de l'historique des transactions.
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

    Notes
    -----
    Ce service agrège les données de transactions pour construire
    des profils clients complets incluant historique et comportement.
    """

    def __init__(self) -> None:
        """Initialiser le service client.

        Notes
        -----
        Instancie le DataLoader pour accéder aux données de transactions.
        """
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
            Numéro de page (default: 1)
        limit : int, optional
            Nombre d'éléments par page (default: 100)

        Returns
        -------
        CustomerListResponse
            Objet contenant :
            - page : Numéro de page actuelle
            - limit : Limite par page
            - total : Nombre total de clients uniques
            - customers : Liste des identifiants clients

        Examples
        --------
        >>> service = CustomerService()
        >>> result = service.get_all_customers(page=1, limit=10)
        >>> print(result.total)
        1234567
        >>> print(len(result.customers))
        10

        Notes
        -----
        Les clients sont identifiés à partir des colonnes nameOrig et nameDest.
        La liste est triée alphabétiquement pour une pagination cohérente.
        """
        df = self.data_loader.get_data()

        # Combiner les clients émetteurs et destinataires
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

    def get_customer_profile(
        self,
        customer_id: str
    ) -> Optional[CustomerProfile]:
        """Récupérer le profil client avec résumé des transactions.

        Parameters
        ----------
        customer_id : str
            Identifiant unique du client

        Returns
        -------
        CustomerProfile or None
            Profil du client incluant :
            - id : Identifiant client
            - transactions_count : Nombre de transactions
            - avg_amount : Montant moyen des transactions
            - total_amount : Volume total transactionné
            - fraudulent : Implication dans des fraudes
            - fraud_count : Nombre de transactions frauduleuses
            
            Retourne None si le client n'existe pas

        Examples
        --------
        >>> service = CustomerService()
        >>> profile = service.get_customer_profile("C1234567890")
        >>> if profile:
        ...     print(profile.transactions_count)
        ...     print(profile.fraudulent)
        42
        False

        Notes
        -----
        Inclut les transactions où le client est émetteur OU destinataire.
        Le flag fraudulent est True si au moins une transaction est frauduleuse.
        """
        df = self.data_loader.get_data()

        # Filtrer toutes les transactions impliquant ce client
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
            Nombre de meilleurs clients à retourner (default: 10)

        Returns
        -------
        List[TopCustomer]
            Liste triée par volume décroissant, contenant :
            - customer_id : Identifiant du client
            - total_volume : Volume total transactionné
            - transaction_count : Nombre de transactions

        Examples
        --------
        >>> service = CustomerService()
        >>> top = service.get_top_customers(n=5)
        >>> print(len(top))
        5
        >>> print(top[0].customer_id)
        'C1823134084'
        >>> print(top[0].total_volume)
        50000000.0

        Notes
        -----
        Le classement prend en compte à la fois les transactions émises
        et reçues pour calculer le volume total de chaque client.
        Utile pour identifier les clients VIP et les comptes à fort volume.
        """
        df = self.data_loader.get_data()

        # Agréger les volumes en tant qu'émetteur
        orig_volume = df.groupby('nameOrig').agg({
            'amount': ['sum', 'count']
        }).reset_index()
        orig_volume.columns = [
            'customer_id',
            'total_volume',
            'transaction_count'
        ]

        # Agréger les volumes en tant que destinataire
        dest_volume = df.groupby('nameDest').agg({
            'amount': ['sum', 'count']
        }).reset_index()
        dest_volume.columns = [
            'customer_id',
            'total_volume',
            'transaction_count'
        ]

        # Combiner et agréger les deux rôles
        combined = pd.concat([orig_volume, dest_volume])

        aggregated = combined.groupby('customer_id').agg({
            'total_volume': 'sum',
            'transaction_count': 'sum'
        }).reset_index()

        # Sélectionner les N meilleurs par volume
        top_customers_df = aggregated.nlargest(n, 'total_volume')

        top_customers = []
        for _, row in top_customers_df.iterrows():
            top_customers.append(TopCustomer(
                customer_id=str(row['customer_id']),
                total_volume=round(float(row['total_volume']), 2),
                transaction_count=int(row['transaction_count'])
            ))

        return top_customers
    