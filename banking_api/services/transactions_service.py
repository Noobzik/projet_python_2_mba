"""
Service de gestion des transactions.

Ce module fournit les fonctionnalités de consultation, filtrage,
recherche et manipulation des transactions bancaires.
"""

from typing import List, Optional

import pandas as pd

from banking_api.models.schemas import (
    Transaction,
    TransactionResponse,
    TransactionSearch,
)
from banking_api.services.data_loader import data_loader


class TransactionsService:
    """
    Service de gestion des transactions.

    Cette classe fournit toutes les opérations liées aux transactions
    bancaires incluant la pagination, le filtrage et la recherche.
    """

    def __init__(self) -> None:
        """Initialise le service des transactions."""
        self.data_loader = data_loader

    def get_all_transactions(
        self,
        page: int = 1,
        limit: int = 100,
        use_chip: Optional[str] = None,
        merchant_state: Optional[str] = None,
        has_errors: Optional[bool] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> TransactionResponse:
        """
        Récupère une liste paginée de transactions avec filtres optionnels.

        Parameters
        ----------
        page : int, optional
            Numéro de la page (défaut: 1)
        limit : int, optional
            Nombre d'éléments par page (défaut: 100)
        use_chip : Optional[str], optional
            Filtre par type d'utilisation de la carte
        merchant_state : Optional[str], optional
            Filtre par état du marchand
        has_errors : Optional[bool], optional
            Filtre par transactions avec erreurs (fraude)
        min_amount : Optional[float], optional
            Montant minimum
        max_amount : Optional[float], optional
            Montant maximum

        Returns
        -------
        TransactionResponse
            Réponse paginée contenant les transactions
        """
        df: pd.DataFrame = self.data_loader.get_transactions().copy()

        # Application des filtres
        if use_chip:
            df = df[df["use_chip"] == use_chip]
        if merchant_state:
            df = df[df["merchant_state"] == merchant_state]
        if has_errors is not None:
            if has_errors:
                df = df[df["errors"].notna()]
            else:
                df = df[df["errors"].isna()]
        if min_amount is not None:
            df = df[df["amount"] >= min_amount]
        if max_amount is not None:
            df = df[df["amount"] <= max_amount]

        total: int = len(df)

        # Pagination
        start_idx: int = (page - 1) * limit
        end_idx: int = start_idx + limit
        paginated_df: pd.DataFrame = df.iloc[start_idx:end_idx]

        # Conversion en modèles Pydantic - remplacer NaN par None
        import numpy as np

        transactions: List[Transaction] = [
            Transaction(**row)
            for row in paginated_df.replace({np.nan: None}).to_dict("records")
        ]

        return TransactionResponse(
            page=page, limit=limit, total=total, transactions=transactions
        )

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        Récupère une transaction par son identifiant.

        Parameters
        ----------
        transaction_id : int
            Identifiant de la transaction

        Returns
        -------
        Optional[Transaction]
            Transaction trouvée ou None
        """
        df: pd.DataFrame = self.data_loader.get_transactions()
        result: pd.DataFrame = df[df["id"] == transaction_id]

        if result.empty:
            return None

        row_dict = result.iloc[0].to_dict()
        # Remplacer NaN par None
        row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
        return Transaction(**row_dict)

    def search_transactions(
        self, search_criteria: TransactionSearch, page: int = 1, limit: int = 100
    ) -> TransactionResponse:
        """
        Recherche de transactions selon des critères multiples.

        Parameters
        ----------
        search_criteria : TransactionSearch
            Critères de recherche
        page : int, optional
            Numéro de page (défaut: 1)
        limit : int, optional
            Nombre d'éléments par page (défaut: 100)

        Returns
        -------
        TransactionResponse
            Résultats paginés de la recherche
        """
        df: pd.DataFrame = self.data_loader.get_transactions().copy()

        # Application des filtres
        if search_criteria.client_id is not None:
            df = df[df["client_id"] == search_criteria.client_id]
        if search_criteria.card_id is not None:
            df = df[df["card_id"] == search_criteria.card_id]
        if search_criteria.amount_range:
            df = df[
                (df["amount"] >= search_criteria.amount_range[0])
                & (df["amount"] <= search_criteria.amount_range[1])
            ]
        if search_criteria.use_chip:
            df = df[df["use_chip"] == search_criteria.use_chip]
        if search_criteria.isFraud is not None:
            if search_criteria.isFraud:
                # Filtre sur les transactions avec erreurs (frauduleuses)
                df = df[df["errors"].notna()]
            else:
                # Filtre sur les transactions sans erreurs
                df = df[df["errors"].isna()]
        if search_criteria.merchant_id is not None:
            df = df[df["merchant_id"] == search_criteria.merchant_id]
        if search_criteria.merchant_state:
            df = df[df["merchant_state"] == search_criteria.merchant_state]
        if search_criteria.mcc is not None:
            df = df[df["mcc"] == search_criteria.mcc]

        total: int = len(df)

        # Pagination
        start_idx: int = (page - 1) * limit
        end_idx: int = start_idx + limit
        paginated_df: pd.DataFrame = df.iloc[start_idx:end_idx]

        import numpy as np

        transactions: List[Transaction] = [
            Transaction(**row)
            for row in paginated_df.replace({np.nan: None}).to_dict("records")
        ]

        return TransactionResponse(
            page=page, limit=limit, total=total, transactions=transactions
        )

    def get_transaction_types(self) -> List[str]:
        """
        Retourne la liste des types d'utilisation de carte disponibles.

        Returns
        -------
        List[str]
            Liste des types d'utilisation
        """
        df: pd.DataFrame = self.data_loader.get_transactions()
        # Retourner les types d'utilisation de carte uniques
        types_list = df["use_chip"].dropna().unique().tolist()
        return [str(t) for t in types_list]

    def get_recent_transactions(self, n: int = 10) -> List[Transaction]:
        """
        Retourne les N dernières transactions.

        Parameters
        ----------
        n : int, optional
            Nombre de transactions à retourner (défaut: 10)

        Returns
        -------
        List[Transaction]
            Liste des dernières transactions
        """
        df: pd.DataFrame = self.data_loader.get_transactions()
        recent_df: pd.DataFrame = df.tail(n)

        import numpy as np

        return [
            Transaction(**row)
            for row in recent_df.replace({np.nan: None}).to_dict("records")
        ]

    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Supprime une transaction (mode test uniquement).

        Parameters
        ----------
        transaction_id : int
            Identifiant de la transaction à supprimer

        Returns
        -------
        bool
            True si la suppression a réussi, False sinon
        """
        # Note: En production, cette méthode devrait être désactivée
        # ou nécessiter des permissions spéciales
        df: pd.DataFrame = self.data_loader.get_transactions()
        initial_len: int = len(df)

        # Filtrage des transactions
        filtered_df: pd.DataFrame = df[df["id"] != transaction_id]

        if len(filtered_df) < initial_len:
            # Mise à jour du DataFrame (en mémoire uniquement)
            self.data_loader._transactions_df = filtered_df
            return True

        return False

    def get_transactions_by_customer(
        self, customer_id: int, as_origin: bool = True
    ) -> List[Transaction]:
        """
        Récupère les transactions d'un client.

        Parameters
        ----------
        customer_id : int
            Identifiant du client
        as_origin : bool, optional
            Paramètre conservé pour compatibilité (ignoré)

        Returns
        -------
        List[Transaction]
            Liste des transactions du client
        """
        df: pd.DataFrame = self.data_loader.get_transactions()
        result_df: pd.DataFrame = df[df["client_id"] == customer_id]

        import numpy as np

        return [
            Transaction(**row)
            for row in result_df.replace({np.nan: None}).to_dict("records")
        ]


# Instance globale du service
transactions_service: TransactionsService = TransactionsService()
