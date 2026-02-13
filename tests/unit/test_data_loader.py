"""Tests unitaires pour le module data loader.
Ce module teste les fonctionnalités de la classe DataLoader.
"""

from pathlib import Path

import pandas as pd
import pytest

from banking_api.utils.data_loader import DataLoader


class TestDataLoader:
    """Suite de tests pour la classe DataLoader."""

    def test_singleton_pattern(self) -> None:
        """Tester que DataLoader suit le pattern Singleton."""
        loader1 = DataLoader()
        loader2 = DataLoader()
        assert loader1 is loader2

    def test_load_data_success(self, temp_csv_file: Path) -> None:
        """Tester le chargement réussi des données depuis un fichier CSV."""
        loader = DataLoader()
        data = loader.load_data(temp_csv_file)

        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert len(data) == 10

    def test_load_data_file_not_found(self) -> None:
        """Tester la gestion d'erreur lorsqu'un fichier est introuvable."""
        loader = DataLoader()
        non_existent_file = Path("non_existent_file.csv")

        with pytest.raises(FileNotFoundError):
            loader.load_data(non_existent_file)

    def test_required_columns_present(self, temp_csv_file: Path) -> None:
        """Tester que toutes les colonnes obligatoires sont présentes."""
        loader = DataLoader()
        data = loader.load_data(temp_csv_file)

        required_columns = [
            "step",
            "type",
            "amount",
            "nameOrig",
            "oldbalanceOrg",
            "newbalanceOrig",
            "nameDest",
            "oldbalanceDest",
            "newbalanceDest",
            "isFraud",
            "isFlaggedFraud",
        ]

        for col in required_columns:
            assert col in data.columns

    def test_data_types_correct(self, temp_csv_file: Path) -> None:
        """Tester que les types de données sont correctement chargés."""
        loader = DataLoader()
        data = loader.load_data(temp_csv_file)

        assert data["step"].dtype in [int, "int64"]
        assert data["amount"].dtype in [float, "float64"]
        assert data["isFraud"].dtype in [int, "int64"]

    def test_get_data_after_load(self, temp_csv_file: Path) -> None:
        """Tester la récupération des données après chargement."""
        loader = DataLoader()
        loader.load_data(temp_csv_file)
        data = loader.get_data()

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 10

    def test_is_loaded_property(self, temp_csv_file: Path) -> None:
        """Tester la propriété is_loaded."""
        loader = DataLoader()
        assert not loader.is_loaded

        loader.load_data(temp_csv_file)
        assert loader.is_loaded

    def test_record_count_property(self, temp_csv_file: Path) -> None:
        """Tester la propriété record_count."""
        loader = DataLoader()
        assert loader.record_count == 0

        loader.load_data(temp_csv_file)
        assert loader.record_count == 10

    def test_reload_data(self, temp_csv_file: Path) -> None:
        """Tester le rechargement des données."""
        loader = DataLoader()
        data1 = loader.load_data(temp_csv_file)
        data2 = loader.reload_data(temp_csv_file)

        assert isinstance(data2, pd.DataFrame)
        assert len(data1) == len(data2)

    def test_cached_data_reuse(self, temp_csv_file: Path) -> None:
        """Tester que les données sont mises en cache et réutilisées."""
        loader = DataLoader()
        data1 = loader.load_data(temp_csv_file)
        data2 = loader.load_data(temp_csv_file)

        assert data1 is data2


# ============================================================================
# NOUVEAUX TESTS POUR ATTEINDRE 100% DE COUVERTURE
# ============================================================================


class TestDataLoaderCoverage:
    """Tests additionnels pour couvrir les lignes 74-75, 78, 88, 113."""

    def test_load_data_invalid_csv_format(self, tmp_path: Path) -> None:
        """Tester le chargement d'un fichier CSV avec un format invalide.

        Couvre les lignes 74-75 : gestion d'erreur lors du parsing CSV.
        """
        # Créer un fichier avec des guillemets non fermés qui causera une ParserError
        invalid_csv = tmp_path / "invalid.csv"
        invalid_csv.write_text(
            "col1,col2,col3\n"
            '"guillemet non fermé,valeur2,valeur3\n'
            "ligne2,valeur4,valeur5\n",
            encoding="utf-8",
        )

        loader = DataLoader()
        loader._data = None  # Reset du singleton

        with pytest.raises(
            ValueError, match="Erreur lors du chargement du fichier CSV"
        ):
            loader.load_data(invalid_csv)

    def test_load_data_empty_dataframe(self, tmp_path: Path) -> None:
        """Tester le chargement d'un CSV vide (seulement les en-têtes).

        Couvre la ligne 78 : vérification que le DataFrame n'est pas vide.
        """
        # Créer un CSV avec seulement les en-têtes, sans données
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text(
            "id,date,client_id,card_id,amount,use_chip,merchant_id,"
            "merchant_city,merchant_state,zip,mcc,errors\n",
            encoding="utf-8",
        )

        loader = DataLoader()
        loader._data = None  # Reset du singleton

        with pytest.raises(ValueError, match="Les données chargées sont vides"):
            loader.load_data(empty_csv)

    def test_load_data_missing_required_columns(self, tmp_path: Path) -> None:
        """Tester le chargement d'un CSV avec des colonnes manquantes.

        Couvre la ligne 88 : vérification des colonnes obligatoires.
        """
        # Créer un CSV avec seulement quelques colonnes (pas toutes)
        incomplete_csv = tmp_path / "incomplete.csv"
        incomplete_csv.write_text(
            "id,date,client_id\n" "1,2023-01-01,123\n", encoding="utf-8"
        )

        loader = DataLoader()
        loader._data = None  # Reset du singleton

        with pytest.raises(ValueError, match="Colonnes obligatoires manquantes"):
            loader.load_data(incomplete_csv)

    def test_adapt_columns_unknown_use_chip_value(self, tmp_path: Path) -> None:
        """Tester l'adaptation des colonnes avec une valeur use_chip inconnue.

        Couvre la ligne 125 : le branch 'else' dans map_transaction_type.
        Cette ligne n'est couverte que si use_chip ne contient ni 'Chip',
        ni 'Swipe', ni 'Online'.
        """
        # Créer un CSV valide avec une valeur use_chip qui ne matche aucune condition
        test_csv = tmp_path / "test_unknown_chip.csv"
        csv_content = (
            "id,date,client_id,card_id,amount,use_chip,merchant_id,"
            "merchant_city,merchant_state,zip,mcc,errors\n"
            "1,2023-01-01,123,456,$100.00,Unknown_Method,789,Paris,FR,75001,5411,\n"
            "2,2023-01-02,124,457,$200.00,Magnetic_Strip,790,Lyon,FR,69001,5812,\n"
        )
        test_csv.write_text(csv_content, encoding="utf-8")

        loader = DataLoader()
        loader._data = None  # Reset du singleton

        df = loader.load_data(test_csv)

        # Vérifier que les valeurs inconnues sont mappées à 'DEBIT' (branch else)
        assert df.loc[0, "type"] == "DEBIT"
        assert df.loc[1, "type"] == "DEBIT"
