"""Configuration Pytest et fixtures partagées.

Ce module fournit des fixtures partagées pour tous les tests.
ADAPTÉ pour le dataset des transactions par carte.
"""

from pathlib import Path
from typing import Generator

import pandas as pd
import pytest

from banking_api.utils.data_loader import DataLoader


@pytest.fixture(scope="session")
def sample_data() -> pd.DataFrame:
    """Créer des données de transactions d'exemple pour les tests.

    Returns
    -------
    pd.DataFrame
        Données de transactions d'exemple avec le NOUVEAU schéma
    """
    # Créer des données qui simulent différents types de transactions
    data = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "date": ["2010-01-01 00:01:00"] * 10,
        "client_id": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        "card_id": [2001, 2002, 2003, 2004, 2005, 2001, 2002, 2003, 2004, 2005],
        "amount": [
            "$100.00",
            "$5000.00",
            "$200000.00",
            "$50.00",
            "$10000.00",
            "$150000.00",
            "$300.00",
            "$75.00",
            "$1000.00",
            "$25000.00",
        ],
        # Faire varier use_chip pour créer différents types
        "use_chip": [
            "Chip Transaction",
            "Swipe Transaction",
            "Swipe Transaction",
            "Chip Transaction",
            "Swipe Transaction",
            "Swipe Transaction",
            "Chip Transaction",
            "Online Transaction",
            "Chip Transaction",
            "Swipe Transaction",
        ],
        "merchant_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "merchant_city": [
            "New York",
            "Los Angeles",
            "Chicago",
            "Houston",
            "Phoenix",
            "New York",
            "Los Angeles",
            "Chicago",
            "Houston",
            "Phoenix",
        ],
        "merchant_state": ["NY", "CA", "IL", "TX", "AZ", "NY", "CA", "IL", "TX", "AZ"],
        "zip": [
            10001.0,
            90001.0,
            60601.0,
            77001.0,
            85001.0,
            10001.0,
            90001.0,
            60601.0,
            77001.0,
            85001.0,
        ],
        "mcc": [5411, 5411, 5411, 5411, 5411, 5411, 5411, 5411, 5411, 5411],
        "errors": [None, None, "Fraud", None, None, "Fraud", None, None, None, "Fraud"],
    }
    return pd.DataFrame(data)


@pytest.fixture(scope="session")
def temp_csv_file(
    tmp_path_factory: pytest.TempPathFactory, sample_data: pd.DataFrame
) -> Path:
    """Créer un fichier CSV temporaire pour les tests.

    Parameters
    ----------
    tmp_path_factory : pytest.TempPathFactory
        Fabrique de chemins temporaires Pytest
    sample_data : pd.DataFrame
        Données de transactions d'exemple

    Returns
    -------
    Path
        Chemin vers le fichier CSV temporaire
    """
    temp_dir = tmp_path_factory.mktemp("data")
    csv_file = temp_dir / "test_transactions.csv"
    sample_data.to_csv(csv_file, index=False)
    return csv_file


@pytest.fixture(autouse=True)
def reset_data_loader() -> Generator[None, None, None]:
    """Réinitialiser le singleton DataLoader entre les tests.

    Yields
    ------
    None
        Contrôle du flux pendant l'exécution des tests
    """
    DataLoader._instance = None
    DataLoader._data = None
    yield
    DataLoader._instance = None
    DataLoader._data = None
