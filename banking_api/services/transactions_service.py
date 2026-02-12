"""Service des transactions pour la logique métier.

Ce module gère toutes les opérations liées aux transactions,
y compris la récupération, le filtrage et la recherche.
"""
import pandas as pd
from typing import Optional
from banking_api.utils.data_loader import DataLoader
from banking_api.models.transaction import (
    TransactionResponse,
    TransactionListResponse,
    TransactionSearchRequest
)
from banking_api.config import DEFAULT_PAGE, DEFAULT_LIMIT, DEFAULT_RECENT_N


class TransactionsService:
    """Classe de service pour les opérations sur les transactions."""

    def __init__(self) -> None:
        """Initialiser le service des transactions."""
        self.data_loader = DataLoader()

    def _df_to_response(self, df: pd.DataFrame) -> list[TransactionResponse]:
        transactions = []
        for idx, row in df.iterrows():
            transactions.append(TransactionResponse(
                id=f"tx_{idx}",
                step=int(row["step"]),
                type=str(row["type"]),
                amount=float(row["amount"]),
                nameOrig=str(row["nameOrig"]),
                newbalanceOrig=float(row["newbalanceOrig"]),
                nameDest=str(row["nameDest"]),
                newbalanceDest=float(row["newbalanceDest"]),
                isFraud=int(row["isFraud"])
            ))
        return transactions

    def get_all_transactions(
        self,
        page: int = DEFAULT_PAGE,
        limit: int = DEFAULT_LIMIT,
        type_filter: Optional[str] = None,
        is_fraud: Optional[int] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> TransactionListResponse:
        df = self.data_loader.get_data().copy()

        if type_filter is not None:
            df = df[df["type"] == type_filter]

        if is_fraud is not None:
            df = df[df["isFraud"] == is_fraud]

        if min_amount is not None:
            df = df[df["amount"] >= min_amount]

        if max_amount is not None:
            df = df[df["amount"] <= max_amount]

        total = len(df)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        df_page = df.iloc[start_idx:end_idx]

        return TransactionListResponse(
            page=page,
            limit=limit,
            total=total,
            transactions=self._df_to_response(df_page)
        )

    def get_transaction_by_id(
        self,
        transaction_id: str
    ) -> Optional[TransactionResponse]:

        if not transaction_id.startswith("tx_"):
            return None

        try:
            idx = int(transaction_id.replace("tx_", ""))
        except ValueError:
            return None

        df = self.data_loader.get_data()

        if idx < 0 or idx >= len(df):
            return None

        row = df.iloc[idx]

        return TransactionResponse(
            id=transaction_id,
            step=int(row["step"]),
            type=str(row["type"]),
            amount=float(row["amount"]),
            nameOrig=str(row["nameOrig"]),
            newbalanceOrig=float(row["newbalanceOrig"]),
            nameDest=str(row["nameDest"]),
            newbalanceDest=float(row["newbalanceDest"]),
            isFraud=int(row["isFraud"])
        )

    def delete_transaction(self, transaction_id: str) -> bool:
        # DELETE ne modifie rien, il valide uniquement l’existence
        return self.get_transaction_by_id(transaction_id) is not None

    def search_transactions(
        self,
        request: TransactionSearchRequest
    ) -> list[TransactionResponse]:
        df = self.data_loader.get_data().copy()

        if request.type is not None:
            df = df[df["type"] == request.type]

        if request.isFraud is not None:
            df = df[df["isFraud"] == request.isFraud]

        if request.amount_range is not None and len(request.amount_range) == 2:
            min_amt, max_amt = request.amount_range
            df = df[(df["amount"] >= min_amt) & (df["amount"] <= max_amt)]

        if request.customer_id is not None:
            df = df[
                (df["nameOrig"] == request.customer_id)
                | (df["nameDest"] == request.customer_id)
            ]

        return self._df_to_response(df)

    def get_transaction_types(self) -> list[str]:
        df = self.data_loader.get_data()
        return sorted(df["type"].unique().tolist())

    def get_recent_transactions(
        self,
        n: int = DEFAULT_RECENT_N
    ) -> list[TransactionResponse]:
        df = self.data_loader.get_data()
        df_sorted = df.sort_values("step", ascending=False)
        df_recent = df_sorted.head(n)
        return self._df_to_response(df_recent)

    def get_transactions_by_customer(
        self,
        customer_id: str
    ) -> list[TransactionResponse]:
        df = self.data_loader.get_data()
        return self._df_to_response(df[df["nameOrig"] == customer_id])

    def get_transactions_to_customer(
        self,
        customer_id: str
    ) -> list[TransactionResponse]:
        df = self.data_loader.get_data()
        return self._df_to_response(df[df["nameDest"] == customer_id])
