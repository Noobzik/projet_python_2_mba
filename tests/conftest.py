"""Configuration pytest et fixtures."""

import os

import pytest
from fastapi.testclient import TestClient

from banking_api.main import app


@pytest.fixture
def client():
    """
    Fixture pour le client de test FastAPI.

    Permet de faire des requêtes HTTP à l'API sans la lancer.
    """
    return TestClient(app)


@pytest.fixture
def sample_fraud_data():
    """Données de test pour la prédiction de fraude."""
    return {
        "type": "Online Transaction",
        "amount": 15000.0,
        "merchant_city": "New York",
        "merchant_state": "NY",
    }


@pytest.fixture
def sample_normal_transaction():
    """Données de test pour une transaction normale."""
    return {
        "type": "Chip Transaction",
        "amount": 50.0,
        "merchant_city": "Paris",
        "merchant_state": "FR",
    }


@pytest.fixture(scope="session", autouse=True)
def setup_test_data(monkeypatch_session):
    """
    Configure les chemins de fichiers pour utiliser les données de test en CI/CD.

    Vérifie si les vrais fichiers de données existent.
    Si non (environnement CI/CD), utilise les fichiers de test minimaux.
    """
    import banking_api.services.data_cache as data_cache
    import banking_api.services.fraud_labels_loader as fraud_labels_loader
    import banking_api.services.transactions_service as transactions_service

    # Chemin vers les vrais fichiers
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    real_csv = os.path.join(base_dir, "data", "transactions_data.csv")
    real_json = os.path.join(base_dir, "data", "train_fraud_labels.json")

    # Si les vrais fichiers n'existent pas (CI/CD), utiliser les fixtures
    if not os.path.exists(real_csv) or not os.path.exists(real_json):
        test_csv = os.path.join(base_dir, "tests", "fixtures", "test_transactions.csv")
        test_json = os.path.join(
            base_dir, "tests", "fixtures", "test_fraud_labels.json"
        )

        # Mock les fonctions de chemin pour utiliser les fichiers de test
        def mock_csv_path():
            return test_csv

        def mock_json_path():
            return test_json

        # Appliquer les mocks
        monkeypatch_session.setattr(
            transactions_service, "_get_csv_path", mock_csv_path
        )
        monkeypatch_session.setattr(
            "banking_api.services.customer_service._get_csv_path", mock_csv_path
        )
        monkeypatch_session.setattr(
            "banking_api.services.stats_service._get_csv_path", mock_csv_path
        )
        monkeypatch_session.setattr(
            "banking_api.services.data_cache._get_csv_path", mock_csv_path
        )

        # Invalider le cache AVANT de mocker pour forcer le rechargement avec les nouvelles données
        if hasattr(data_cache.get_cached_dataframe, "cache_clear"):
            data_cache.get_cached_dataframe.cache_clear()
        if hasattr(fraud_labels_loader.load_fraud_labels, "cache_clear"):
            fraud_labels_loader.load_fraud_labels.cache_clear()

        # Mock le chargement des labels de fraude
        def mock_load_fraud_labels():
            import json

            with open(test_json, "r") as f:
                data = json.load(f)
            return data.get("target", {})

        monkeypatch_session.setattr(
            fraud_labels_loader, "load_fraud_labels", mock_load_fraud_labels
        )


@pytest.fixture(scope="session")
def monkeypatch_session():
    """Monkeypatch pour toute la session de test."""
    from _pytest.monkeypatch import MonkeyPatch

    m = MonkeyPatch()
    yield m
    m.undo()
