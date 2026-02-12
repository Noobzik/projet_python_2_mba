"""Tests unitaires pour le module data loader.

Ce module teste les fonctionnalités de la classe DataLoader.
"""
import pytest
import pandas as pd
from pathlib import Path
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
        """Tester la gestion d’erreur lorsqu’un fichier est introuvable."""
        loader = DataLoader()
        non_existent_file = Path("non_existent_file.csv")
        
        with pytest.raises(FileNotFoundError):
            loader.load_data(non_existent_file)
    
    def test_required_columns_present(self, temp_csv_file: Path) -> None:
        """Tester que toutes les colonnes obligatoires sont présentes."""
        loader = DataLoader()
        data = loader.load_data(temp_csv_file)
        
        required_columns = [
            'step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg',
            'newbalanceOrig', 'nameDest', 'oldbalanceDest',
            'newbalanceDest', 'isFraud', 'isFlaggedFraud'
        ]
        
        for col in required_columns:
            assert col in data.columns
    
    def test_data_types_correct(self, temp_csv_file: Path) -> None:
        """Tester que les types de données sont correctement chargés."""
        loader = DataLoader()
        data = loader.load_data(temp_csv_file)
        
        assert data['step'].dtype in [int, 'int64']
        assert data['amount'].dtype in [float, 'float64']
        assert data['isFraud'].dtype in [int, 'int64']
    
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