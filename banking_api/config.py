"""Module de configuration pour l’API des transactions bancaires.

Ce module contient tous les paramètres et réglages
de configuration de l’application.
"""
from pathlib import Path
from typing import Final

# Répertoire racine
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent

# Configuration des données
DATA_DIR: Final[Path] = BASE_DIR / "data"
DATA_FILE: Final[Path] = DATA_DIR / "transactions_data.csv"

# Configuration de l’API
API_VERSION: Final[str] = "1.0.0"
API_TITLE: Final[str] = "Banking Transactions API"
API_DESCRIPTION: Final[str] = """
API REST complète pour l'exposition et la manipulation des données
de transactions bancaires avec détection de fraude.
"""

# Paramètres par défaut de pagination
DEFAULT_PAGE: Final[int] = 1
DEFAULT_LIMIT: Final[int] = 50
MAX_LIMIT: Final[int] = 1000

# Valeur par défaut pour les transactions récentes
DEFAULT_RECENT_N: Final[int] = 10

# Valeur par défaut pour les meilleurs clients
DEFAULT_TOP_N: Final[int] = 10

# Intervalles de distribution des montants
AMOUNT_BINS: Final[list[str]] = [
    "0-100",
    "100-500",
    "500-1000",
    "1000-5000",
    "5000-10000",
    "10000-50000",
    "50000+"
]

# Seuils de détection de fraude
FRAUD_THRESHOLD: Final[float] = 0.5
HIGH_RISK_AMOUNT: Final[float] = 200000.0

# Métadonnées système
LAST_UPDATE: Final[str] = "2025-12-20T22:00:00Z"
