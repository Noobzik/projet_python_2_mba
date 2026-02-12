"""
Tests unitaires pour le DataLoader.
"""

import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

import pandas as pd

from banking_api.services.data_loader import DataLoader


class TestDataLoader(unittest.TestCase):
    """Tests pour le DataLoader."""

    def setUp(self) -> None:
        """Configuration initiale des tests."""
        # Réinitialiser le singleton
        DataLoader._instance = None

    def tearDown(self) -> None:
        """Nettoyage après les tests."""
        DataLoader._instance = None

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.cwd")
    def test_init_default_path(self, mock_cwd, mock_exists) -> None:
        """Test de l'initialisation avec le chemin par défaut."""
        mock_cwd.return_value = Path("/cwd")
        mock_exists.return_value = False  # CWD/data n'existe pas

        loader = DataLoader()
        # Devrait utiliser le package path
        self.assertTrue(str(loader.data_path).endswith("data"))

    @patch("os.environ.get")
    @patch("pathlib.Path.exists")
    def test_init_env_path(self, mock_exists, mock_env_get) -> None:
        """Test de l'initialisation avec une variable d'environnement."""
        mock_env_get.return_value = "/env/data"
        mock_exists.return_value = True

        loader = DataLoader()
        self.assertEqual(str(loader.data_path), "\\env\\data")  # Windows path separator

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_data_success(self, mock_exists, mock_read_csv) -> None:
        """Test de chargement des données avec succès."""
        mock_exists.return_value = True

        # Mock des DataFrames retournés
        mock_transactions = pd.DataFrame(
            {
                "id": [1],
                "amount": ["$100.0"],
                "client_id": [1],
                "card_id": [1],
                "merchant_id": [1],
                "mcc": [1],
                "zip": [90001],
                "errors": [None],
                "use_chip": [None],
            }
        )
        mock_users = pd.DataFrame({"id": [1]})
        mock_cards = pd.DataFrame({"id": [1]})

        mock_read_csv.side_effect = [mock_transactions, mock_users, mock_cards]

        # Mock json load
        with patch("builtins.open", mock_open(read_data='{"key": "value"}')):
            with patch("json.load", return_value={"key": "value"}):
                loader = DataLoader()
                loader.load_data()

                self.assertIsNotNone(loader._transactions_df)
                self.assertIsNotNone(loader._users_df)
                self.assertIsNotNone(loader._cards_df)
                self.assertIsNotNone(loader._fraud_labels)
                self.assertIsNotNone(loader._mcc_codes)

                # Vérifier le nettoyage des données
                df = loader._transactions_df
                self.assertEqual(df["amount"].iloc[0], 100.0)  # $ retiré
                self.assertEqual(df["use_chip"].iloc[0], "UNKNOWN")  # NaN remplacé

    @patch("pathlib.Path.exists")
    def test_load_data_file_not_found(self, mock_exists) -> None:
        """Test d'erreur si le fichier de transactions n'existe pas."""
        mock_exists.return_value = False

        loader = DataLoader()
        with self.assertRaises(FileNotFoundError):
            loader.load_data()

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_get_transactions(self, mock_exists, mock_read_csv) -> None:
        """Test de récupération des transactions."""
        mock_exists.return_value = True
        mock_read_csv.return_value = pd.DataFrame({"id": [1]})

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value={}):
                loader = DataLoader()
                df = loader.get_transactions()
                self.assertIsInstance(df, pd.DataFrame)

                # Deuxième appel devrait retourner le cache
                df2 = loader.get_transactions()
                self.assertIs(df, df2)

    def test_get_transactions_not_loaded(self) -> None:
        """Test d'erreur si les transactions ne sont pas chargées."""
        loader = DataLoader()
        # On force _transactions_df à None et on mock load_data pour ne rien faire
        loader._transactions_df = None
        with patch.object(loader, "load_data"):
            # Si load_data ne fait rien, get_transactions devrait lever une erreur
            with self.assertRaises(ValueError):
                loader.get_transactions()

    def test_getters(self) -> None:
        """Test des getters simples."""
        loader = DataLoader()
        loader._users_df = pd.DataFrame()
        loader._cards_df = pd.DataFrame()
        loader._fraud_labels = {}
        loader._mcc_codes = {}

        self.assertIsNotNone(loader.get_users())
        self.assertIsNotNone(loader.get_cards())
        self.assertIsNotNone(loader.get_fraud_labels())
        self.assertIsNotNone(loader.get_mcc_codes())

    def test_is_loaded(self) -> None:
        """Test de is_loaded."""
        loader = DataLoader()
        self.assertFalse(loader.is_loaded())
        loader._transactions_df = pd.DataFrame()
        self.assertTrue(loader.is_loaded())
