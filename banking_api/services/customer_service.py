"""
Service de gestion des clients.

Ce module fournit les fonctionnalités d'agrégation et d'analyse
des données clients basées sur leurs transactions.
"""

from typing import Any, Dict, List, Optional, cast

import pandas as pd

from banking_api.models.schemas import Customer, CustomerListResponse
from banking_api.services.data_loader import data_loader


class CustomerService:
    """
    Service de gestion des clients.

    Cette classe fournit les opérations d'analyse et de consultation
    des profils clients basés sur leurs transactions.
    """

    def __init__(self) -> None:
        """Initialise le service des clients."""
        self.data_loader = data_loader

    def get_all_customers(
        self, page: int = 1, limit: int = 100
    ) -> CustomerListResponse:
        """
        Récupère une liste paginée des clients.

        Parameters
        ----------
        page : int, optional
            Numéro de page (défaut: 1)
        limit : int, optional
            Nombre d'éléments par page (défaut: 100)

        Returns
        -------
        CustomerListResponse
            Réponse paginée contenant les identifiants clients
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        # Extraction des clients uniques
        unique_customers: List[int] = sorted(df["client_id"].unique().tolist())
        total: int = len(unique_customers)

        # Pagination
        start_idx: int = (page - 1) * limit
        end_idx: int = start_idx + limit
        paginated_customers: List[int] = unique_customers[start_idx:end_idx]

        return CustomerListResponse(
            page=page, limit=limit, total=total, customers=paginated_customers
        )

    def get_customer_profile(self, customer_id: int) -> Optional[Customer]:
        """
        Récupère le profil d'un client.

        Parameters
        ----------
        customer_id : int
            Identifiant du client

        Returns
        -------
        Optional[Customer]
            Profil du client ou None si non trouvé
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        # Transactions du client
        customer_transactions: pd.DataFrame = df[df["client_id"] == customer_id]

        if customer_transactions.empty:
            return None

        transactions_count: int = len(customer_transactions)
        avg_amount: float = float(customer_transactions["amount"].mean())
        total_amount: float = float(customer_transactions["amount"].sum())
        # Note: isFraud n'existe plus, on utilise la colonne 'errors' pour détecter la fraude
        fraudulent: bool = bool(
            customer_transactions["errors"].notna().sum() > 0
            if "errors" in customer_transactions.columns
            else False
        )

        return Customer(
            id=customer_id,
            transactions_count=transactions_count,
            avg_amount=round(avg_amount, 2),
            total_amount=round(total_amount, 2),
            fraudulent=fraudulent,
        )

    def get_top_customers(self, n: int = 10, by: str = "volume") -> List[Customer]:
        """
        Récupère le top N des clients.

        Parameters
        ----------
        n : int, optional
            Nombre de clients à retourner (défaut: 10)
        by : str, optional
            Critère de classement: 'volume' ou 'count' (défaut: 'volume')

        Returns
        -------
        List[Customer]
            Liste des meilleurs clients
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        # Agrégation par client
        agg_dict: Dict[str, Any] = {
            "amount": ["count", "mean", "sum"],
        }
        # Ajouter errors si disponible pour détecter la fraude
        if "errors" in df.columns:
            agg_dict["errors"] = lambda x: x.notna().sum() > 0

        customer_stats: pd.DataFrame = (
            df.groupby("client_id").agg(agg_dict).reset_index()
        )

        # Renommage des colonnes
        if "errors" in df.columns:
            customer_stats.columns = [
                "customer_id",
                "transactions_count",
                "avg_amount",
                "total_amount",
                "fraudulent",
            ]
        else:
            customer_stats.columns = [
                "customer_id",
                "transactions_count",
                "avg_amount",
                "total_amount",
            ]
            customer_stats["fraudulent"] = False

        # Tri selon le critère
        if by == "count":
            customer_stats = customer_stats.sort_values(
                "transactions_count", ascending=False
            )
        else:  # volume
            customer_stats = customer_stats.sort_values("total_amount", ascending=False)

        # Sélection du top N
        top_customers_df: pd.DataFrame = customer_stats.head(n)

        # Conversion en modèles
        top_customers: List[Customer] = []
        for _, row in top_customers_df.iterrows():
            customer: Customer = Customer(
                id=int(row["customer_id"]),
                transactions_count=int(row["transactions_count"]),
                avg_amount=round(float(row["avg_amount"]), 2),
                total_amount=round(float(row["total_amount"]), 2),
                fraudulent=bool(row["fraudulent"]),
            )
            top_customers.append(customer)

        return top_customers

    def get_customer_transaction_history(
        self, customer_id: int, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des transactions d'un client.

        Parameters
        ----------
        customer_id : int
            Identifiant du client
        limit : int, optional
            Nombre maximum de transactions (défaut: 100)

        Returns
        -------
        List[Dict[str, Any]]
            Liste des transactions du client
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        # Transactions du client
        customer_df: pd.DataFrame = df[df["client_id"] == customer_id]

        # Limitation
        customer_df = customer_df.head(limit)

        return cast(List[Dict[str, Any]], customer_df.to_dict("records"))

    def get_customer_statistics(self, customer_id: int) -> Dict[str, Any]:
        """
        Calcule des statistiques détaillées pour un client.

        Parameters
        ----------
        customer_id : int
            Identifiant du client

        Returns
        -------
        Dict[str, Any]
            Dictionnaire des statistiques détaillées
        """
        df: pd.DataFrame = self.data_loader.get_transactions()

        # Transactions du client
        client_df: pd.DataFrame = df[df["client_id"] == customer_id]

        if client_df.empty:
            return {}

        # Statistiques par état de marchand
        top_states = client_df["merchant_state"].value_counts().head(3).to_dict()

        stats: Dict[str, Any] = {
            "customer_id": customer_id,
            "total_transactions": len(client_df),
            "total_amount": round(float(client_df["amount"].sum()), 2),
            "avg_amount": round(float(client_df["amount"].mean()), 2),
            "min_amount": round(float(client_df["amount"].min()), 2),
            "max_amount": round(float(client_df["amount"].max()), 2),
            "fraud_involved": bool(
                client_df["errors"].notna().sum() > 0
                if "errors" in client_df.columns
                else False
            ),
            "most_used_chip_method": (
                str(client_df["use_chip"].mode()[0])
                if not client_df["use_chip"].mode().empty
                else "UNKNOWN"
            ),
            "top_merchant_states": {str(k): int(v) for k, v in top_states.items()},
            "unique_cards": int(client_df["card_id"].nunique()),
            "unique_merchants": int(client_df["merchant_id"].nunique()),
        }

        return stats


# Instance globale du service
customer_service: CustomerService = CustomerService()
