from __future__ import annotations
import pandas as pd
from unittest.mock import patch
from banking_api.services import dataset_loader

def test_load_dataset_integration(tmp_path):
    """
    Teste le chargement complet :
    1. Simule le téléchargement Kaggle.
    2. Vérifie le nettoyage (Renommage colonnes, devise, simulation temps).
    """
    
    # 1. On vide le cache pour forcer un rechargement propre
    dataset_loader._DATAFRAME_CACHE = None

    # 2. On crée un FAUX fichier CSV brut (format Kaggle sale)
    # C'est ce fichier que le loader va "nettoyer"
    csv_path = tmp_path / "transactions_data.csv"
    raw_data = {
        "id": ["unk"],                # Sera ignoré ou transformé
        "client_id": ["C_TEST"],      # Deviendra nameOrig
        "merchant_id": ["M_TEST"],    # Deviendra nameDest
        "amount": ["($50.00)"],       # Deviendra 50.0 (Format sale)
        "use_chip": ["Swipe Transaction"], # Deviendra PAYMENT
        "errors": ["Error?"]          # Deviendra isFraud = 1
    }
    pd.DataFrame(raw_data).to_csv(csv_path, index=False)

    # 3. LA MAGIE (Mocking)
    # On remplace 'kagglehub.dataset_download' par une fonction qui renvoie notre dossier temporaire
    with patch("kagglehub.dataset_download", return_value=str(tmp_path)):
        # On appelle la fonction comme si de rien n'était
        df = dataset_loader.load_dataset()

    # 4. VÉRIFICATIONS (Le nettoyage a-t-il fonctionné ?)
    assert df is not None
    assert not df.empty
    
    # Le loader doit avoir renommé 'client_id' en 'nameOrig'
    assert "nameOrig" in df.columns
    assert df.iloc[0]["nameOrig"] == "C_TEST"
    
    # Le loader doit avoir nettoyé l'argent : "($50.00)" -> 50.0
    assert df.iloc[0]["amount"] == 50.0
    
    # Le loader doit avoir traduit le type : "Swipe Transaction" -> "PAYMENT"
    assert df.iloc[0]["type"] == "PAYMENT"
    
    # Le loader doit avoir généré un 'step' aléatoire (1 à 30)
    assert 1 <= df.iloc[0]["step"] <= 30

def test_get_status_loaded(tmp_path):
    """Vérifie que le statut passe à True après chargement."""
    
    # On prépare le terrain
    dataset_loader._DATAFRAME_CACHE = None
    csv_path = tmp_path / "transactions_data.csv"
    pd.DataFrame({"client_id": ["A"], "amount": ["10"]}).to_csv(csv_path)

    # On charge
    with patch("kagglehub.dataset_download", return_value=str(tmp_path)):
        dataset_loader.load_dataset()
    
    # On vérifie le statut
    status = dataset_loader.get_status()
    assert status.loaded is True
    assert status.rows > 0