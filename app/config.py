from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "transaction_data.csv"

def connexion_dataset():
    return pd.read_csv(DATASET_PATH)


