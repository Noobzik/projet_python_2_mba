"""Routes pour la gestion des clients."""

from fastapi import APIRouter, HTTPException

from banking_api.services.data_cache import get_cached_dataframe

router = APIRouter()


@router.get("", response_model=dict)
def get_customers(skip: int = 0, limit: int = 100) -> dict:
    """
    Récupère la liste des clients avec pagination.

    Args:
        skip: Nombre de clients à sauter (pour la pagination)
        limit: Nombre maximum de clients à retourner (max 1000)

    Returns:
        dict: Liste paginée des clients avec métadonnées
    """
    if limit > 1000:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 1000")

    df = get_cached_dataframe()

    # Grouper par client_id
    customer_groups = (
        df.groupby("client_id")
        .agg({"amount": ["count", "mean"], "isFraud": "sum"})
        .reset_index()
    )

    customer_groups.columns = [
        "customer_id",
        "transaction_count",
        "avg_amount",
        "fraud_count",
    ]
    customer_groups["fraudulent"] = customer_groups["fraud_count"] > 0

    # Pagination
    total_customers = len(customer_groups)
    paginated_customers = customer_groups.iloc[skip : skip + limit]

    customers = [
        {
            "id": str(row["customer_id"]),
            "transaction_count": int(row["transaction_count"]),
            "avg_amount": round(row["avg_amount"], 2),
            "fraud_count": int(row["fraud_count"]),
            "fraudulent": bool(row["fraudulent"]),
        }
        for _, row in paginated_customers.iterrows()
    ]

    return {
        "customers": customers,
        "total": total_customers,
        "skip": skip,
        "limit": limit,
        "returned": len(customers),
    }


@router.get("/top", response_model=list)
def get_top_customers(limit: int = 10) -> list:
    """
    Récupère les meilleurs clients.

    Args:
        limit: Nombre de clients à retourner

    Returns:
        list: Liste des meilleurs clients
    """
    df = get_cached_dataframe()

    # Grouper par client_id
    customer_groups = (
        df.groupby("client_id")
        .agg({"amount": ["count", "mean"], "isFraud": "sum"})
        .reset_index()
    )

    customer_groups.columns = [
        "customer_id",
        "transaction_count",
        "avg_amount",
        "fraud_count",
    ]
    customer_groups["fraudulent"] = customer_groups["fraud_count"] > 0

    # Trier par nombre de transactions
    top_customers = customer_groups.nlargest(limit, "transaction_count")

    return [
        {
            "customer_id": int(row["customer_id"]),
            "transaction_count": int(row["transaction_count"]),
            "avg_amount": round(row["avg_amount"], 2),
            "fraud_count": int(row["fraud_count"]),
            "fraudulent": bool(row["fraudulent"]),
        }
        for _, row in top_customers.iterrows()
    ]


@router.get("/{customer_id}", response_model=dict)
def get_customer_profile(customer_id: str) -> dict:
    """
    Récupère le profil d'un client.

    Args:
        customer_id: ID du client

    Returns:
        dict: Profil du client
    """
    df = get_cached_dataframe()

    # Filtrer les transactions du client
    customer_df = df[df["client_id"] == int(customer_id)]

    if customer_df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Calculer les statistiques
    total_transactions = len(customer_df)
    avg_amount = customer_df["amount"].mean()
    fraud_count = int(customer_df["isFraud"].sum())
    fraudulent = fraud_count > 0

    return {
        "id": customer_id,
        "transaction_count": total_transactions,
        "avg_amount": round(avg_amount, 2),
        "fraud_count": fraud_count,
        "fraudulent": fraudulent,
    }
