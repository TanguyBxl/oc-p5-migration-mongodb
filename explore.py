import pandas as pd
df = pd.read_csv("data/healthcare_dataset.csv")

print(f"--- DIMENSIONS : {df.shape[0]} lignes, {df.shape[1]} colonnes ---")
print("\n--- TYPES ET VALEURS NON-NULLES ---")
print(df.info())

print("\n--- VALEURS MANQUANTES ---")
print(df.isna().sum())

print(f"\n--- DOUBLONS EXACTS : {df.duplicated().sum()} ---")
print("\n--- APERÇU DES 3 PREMIÈRES LIGNES ---")
print(df.head(3).to_string())