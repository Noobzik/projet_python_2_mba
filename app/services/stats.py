import pandas as pd
from typing import Dict, List, Optional, Union
from app.config import connexion_dataset

# Chargement global du dataset
df = connexion_dataset()


def stats_by_type(df: pd.DataFrame) -> List[Dict[str, Union[str, float]]]:
    
    grouped = (
        df.groupby("Transaction Type")["Transaction Amount"]
        .agg(count="count", avg_amount="mean")
        .reset_index()
    )

    return grouped.to_dict(orient="records")


def amount_distribution(
    df: pd.DataFrame,
    bins: Optional[List[float]] = None
) -> Dict[str, List]:
    
    if bins is None:
        bins = [0, 100, 500, 1000, 5000, float("inf")]

    labels = [
        f"{int(bins[i])}-{int(bins[i + 1]) if bins[i + 1] != float('inf') else 'plus'}"
        for i in range(len(bins) - 1)
    ]

    counts = (
        pd.cut(df["Transaction Amount"], bins=bins, labels=labels)
        .value_counts()
        .sort_index()
    )

    return {
        "bins": labels,
        "counts": counts.tolist()
    }
