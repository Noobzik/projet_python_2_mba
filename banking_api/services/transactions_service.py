"""Service de gestion des transactions bancaires."""

import os
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import HTTPException


def _get_csv_path() -> str:
    """
    Retourne le chemin vers le fichier CSV de transactions.

    Returns
    -------
    str
        Chemin absolu vers le fichier CSV
    """
    base_dir: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    csv_path: str = os.path.join(base_dir, "data", "transactions_data.csv")
    return csv_path


def _convert_transaction_types(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convertit les types de données d'une transaction.

    Parameters
    ----------
    transaction : Dict[str, Any]
        Transaction avec des valeurs en string

    Returns
    -------
    Dict[str, Any]
        Transaction avec des types corrects
    """
    # Clean amount: remove $ and convert to float
    amount_str = str(transaction["amount"]).replace("$", "").replace(",", "")
    amount = float(amount_str)

    # Determine if transaction is fraudulent based on errors column
    is_fraud = (
        1
        if pd.notna(transaction.get("errors"))
        and str(transaction.get("errors")).strip() != ""
        else 0
    )

    return {
        "id": int(transaction["id"]),
        "date": str(transaction["date"]),
        "client_id": int(transaction["client_id"]),
        "card_id": int(transaction["card_id"]),
        "amount": amount,
        "use_chip": str(transaction["use_chip"]),
        "merchant_id": int(transaction["merchant_id"]),
        "merchant_city": str(transaction["merchant_city"]),
        "merchant_state": str(transaction["merchant_state"]),
        "zip": str(transaction.get("zip", "")),
        "mcc": str(transaction.get("mcc", "")),
        "errors": str(transaction.get("errors", "")),
        "isFraud": is_fraud,
    }


def get_paginated_transactions(
    page: int,
    limit: int,
    type_filter: Optional[str] = None,
    is_fraud: Optional[int] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Retourne une liste paginée de transactions avec filtres optionnels.

    Parameters
    ----------
    page : int
        Numéro de la page
    limit : int
        Nombre de transactions par page
    type_filter : Optional[str]
        Filtrer par type de transaction
    is_fraud : Optional[int]
        Filtrer par fraude (0 ou 1)
    min_amount : Optional[float]
        Montant minimum
    max_amount : Optional[float]
        Montant maximum

    Returns
    -------
    Dict[str, Any]
        Dictionnaire contenant page, total, et transactions
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        df: pd.DataFrame = pd.read_csv(csv_path)

        # Clean amount column: remove $ and convert to float
        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace("$", "")
            .str.replace(",", "")
            .astype(float)
        )

        # Add fraud detection based on errors column
        df["isFraud"] = df["errors"].apply(
            lambda x: 1 if pd.notna(x) and str(x).strip() != "" else 0
        )

        # Appliquer les filtres
        if type_filter:
            # Use 'use_chip' as type since this dataset doesn't have 'type'
            df = df[df["use_chip"] == type_filter]
        if is_fraud is not None:
            df = df[df["isFraud"] == is_fraud]
        if min_amount is not None:
            df = df[df["amount"] >= min_amount]
        if max_amount is not None:
            df = df[df["amount"] <= max_amount]

        total: int = len(df)
        start_idx: int = (page - 1) * limit
        end_idx: int = start_idx + limit

        transactions: List[Dict[str, Any]] = df.iloc[start_idx:end_idx].to_dict(
            "records"
        )

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "transactions": transactions,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la lecture: {str(e)}"
        )


def get_transaction_by_id(transaction_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère une transaction par son ID.

    Parameters
    ----------
    transaction_id : str
        L'identifiant de la transaction (colonne id du CSV)

    Returns
    -------
    Optional[Dict[str, Any]]
        La transaction trouvée ou None
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        df: pd.DataFrame = pd.read_csv(csv_path)

        # Clean amount column
        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace("$", "")
            .str.replace(",", "")
            .astype(float)
        )

        # Add fraud detection
        df["isFraud"] = df["errors"].apply(
            lambda x: 1 if pd.notna(x) and str(x).strip() != "" else 0
        )

        # Search by transaction ID (column 'id')
        transaction_id_int: int = int(transaction_id)
        matching_rows = df[df["id"] == transaction_id_int]

        if len(matching_rows) == 0:
            return None

        transaction: Dict[str, Any] = matching_rows.iloc[0].to_dict()
        return transaction
    except ValueError:
        return None
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la lecture: {str(e)}"
        )


def get_transaction_types() -> List[str]:
    """
    Retourne la liste des types de transactions uniques.

    Returns
    -------
    List[str]
        Liste des types de transactions
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        df: pd.DataFrame = pd.read_csv(csv_path)
        # Use 'use_chip' column as transaction type
        types: List[str] = df["use_chip"].unique().tolist()
        return types
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la lecture: {str(e)}"
        )


def get_recent_transactions(n: int = 10) -> List[Dict[str, Any]]:
    """
    Retourne les N dernières transactions du dataset.

    Parameters
    ----------
    n : int
        Nombre de transactions à retourner (défaut: 10)

    Returns
    -------
    List[Dict[str, Any]]
        Liste des dernières transactions
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        # Use Unix tail command for fast access to last N lines
        import io
        import subprocess

        # Get header first
        with open(csv_path, "r") as f:
            header = f.readline()

        # Get last n lines using tail (much faster than reading entire file)
        result = subprocess.run(
            ["tail", f"-{n}", csv_path], capture_output=True, text=True
        )

        # Combine header with last n lines
        csv_content = header + result.stdout

        # Read into DataFrame
        df: pd.DataFrame = pd.read_csv(io.StringIO(csv_content))

        # Clean amount column
        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace("$", "")
            .str.replace(",", "")
            .astype(float)
        )

        # Add fraud detection
        df["isFraud"] = df["errors"].apply(
            lambda x: 1 if pd.notna(x) and str(x).strip() != "" else 0
        )

        recent: List[Dict[str, Any]] = df.to_dict("records")
        return recent
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la lecture: {str(e)}"
        )


def search_transactions(
    type_filter: Optional[str] = None,
    is_fraud: Optional[int] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Recherche multicritère de transactions.

    Parameters
    ----------
    type_filter : Optional[str]
        Type de transaction
    is_fraud : Optional[int]
        Indicateur de fraude (0 ou 1)
    amount_min : Optional[float]
        Montant minimum
    amount_max : Optional[float]
        Montant maximum

    Returns
    -------
    List[Dict[str, Any]]
        Liste des transactions correspondant aux critères
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        df: pd.DataFrame = pd.read_csv(csv_path)

        # Clean amount column
        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace("$", "")
            .str.replace(",", "")
            .astype(float)
        )

        # Add fraud detection
        df["isFraud"] = df["errors"].apply(
            lambda x: 1 if pd.notna(x) and str(x).strip() != "" else 0
        )

        if type_filter:
            df = df[df["use_chip"] == type_filter]
        if is_fraud is not None:
            df = df[df["isFraud"] == is_fraud]
        if amount_min is not None:
            df = df[df["amount"] >= amount_min]
        if amount_max is not None:
            df = df[df["amount"] <= amount_max]

        results: List[Dict[str, Any]] = df.to_dict("records")
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la recherche: {str(e)}"
        )


def get_transactions_by_customer(customer_id: str) -> List[Dict[str, Any]]:
    """
    Récupère toutes les transactions émises par un client.

    Parameters
    ----------
    customer_id : str
        Identifiant du client (client_id)

    Returns
    -------
    List[Dict[str, Any]]
        Liste des transactions du client
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        df: pd.DataFrame = pd.read_csv(csv_path)
        customer_transactions: pd.DataFrame = df[df["client_id"] == int(customer_id)]
        results: List[Dict[str, Any]] = customer_transactions.to_dict("records")
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la lecture: {str(e)}"
        )


def get_transactions_to_customer(customer_id: str) -> List[Dict[str, Any]]:
    """
    Récupère toutes les transactions reçues par un client.

    Parameters
    ----------
    customer_id : str
        Identifiant du marchand destinataire (merchant_id)

    Returns
    -------
    List[Dict[str, Any]]
        Liste des transactions reçues
    """
    csv_path: str = _get_csv_path()

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier de données non trouvé")

    try:
        df: pd.DataFrame = pd.read_csv(csv_path)
        customer_transactions: pd.DataFrame = df[df["merchant_id"] == int(customer_id)]
        results: List[Dict[str, Any]] = customer_transactions.to_dict("records")
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la lecture: {str(e)}"
        )


def delete_transaction(transaction_id: str) -> Dict[str, str]:
    """
    Supprime une transaction (mode test uniquement).

    Parameters
    ----------
    transaction_id : str
        Identifiant de la transaction à supprimer

    Returns
    -------
    Dict[str, str]
        Message de confirmation
    """
    # En mode test/fictif, on simule juste la suppression
    return {"message": f"Transaction {transaction_id} supprimée (mode test)"}
