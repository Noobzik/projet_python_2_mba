import pandas as pd
def connexion_dataset():
    # Chargement du dataset 
    DATASET_PATH = "C:/Users/DELL/Documents/workspace/projet_python_2_mba/app/data/transaction_data.csv"
    df = pd.read_csv(DATASET_PATH)
    return df