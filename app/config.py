import pandas as pd
def connexion_dataset():
    # Chargement du dataset 
    DATASET_PATH = "C:/Users/carol/Documents/transaction_data.csv"
    df = pd.read_csv(DATASET_PATH)
    return df