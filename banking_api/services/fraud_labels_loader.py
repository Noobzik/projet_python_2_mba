"""Utilitaire pour charger les labels de fraude depuis le JSON."""

import json
import os
from functools import lru_cache
from typing import Dict


@lru_cache(maxsize=1)
def load_fraud_labels() -> Dict[str, str]:
    """
    Charge les labels de fraude depuis le fichier JSON.

    Utilise un cache pour ne charger le fichier qu'une seule fois.

    Returns
    -------
    Dict[str, str]
        Dictionnaire avec les IDs de transaction comme clés et "Yes"/"No" comme valeurs
    """
    base_dir: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    json_path: str = os.path.join(base_dir, "data", "train_fraud_labels.json")

    if not os.path.exists(json_path):
        # Si le fichier n'existe pas, retourner un dictionnaire vide
        return {}

    with open(json_path, "r") as f:
        data = json.load(f)

    return data.get("target", {})


def is_fraud(transaction_id: str) -> int:
    """
    Vérifie si une transaction est frauduleuse.

    Parameters
    ----------
    transaction_id : str
        L'identifiant de la transaction

    Returns
    -------
    int
        1 si fraude, 0 sinon
    """
    labels: Dict[str, str] = load_fraud_labels()
    label: str = labels.get(str(transaction_id), "No")
    return 1 if label == "Yes" else 0
