#%%

import pandas as pd
df = pd.read_csv("data/healthcare_dataset.csv")

# 1. Noms de colonnes en minuscules
df.columns = df.columns.str.lower().str.strip()

# 2. Valeurs de toutes les colonnes texte en minuscules
for col in df.select_dtypes(include="str").columns:
    df[col] = df[col].str.strip().str.lower()


# %%
display(df.head(10))
# %%
df.dtypes
# %%
df["date of admission"] = pd.to_datetime(df["date of admission"])
df["discharge date"] = pd.to_datetime(df["discharge date"])


# %%
df.dtypes
# %%
df.duplicated().sum()
# %%
df = df.drop_duplicates()
# %%
display(df.describe())
# %%
df["billing amount"] = df["billing amount"].round(2)

display(df.describe())
# %%
display(df.head(3))
# %%
print((df["billing amount"] < 0).sum())
# %%
# 1. Récupérer la liste des noms ayant au moins un montant négatif
patients_negatifs = df[df["billing amount"] < 0]["name"].unique()

# 2. Afficher toutes les lignes de ces patients triées par nom et date
display(
    df[df["name"].isin(patients_negatifs)]
    .sort_values(by=["name", "date of admission"])
    .head(20)
)
# Conclusion: les transactions négatives sont dues à des remboursements, donc pas de problème.
# %%
# Remplacer les espaces des colonnes par des underscores (ex: "billing_amount")
df.columns = df.columns.str.replace(" ", "_")

# Convertir chaque ligne du DataFrame en dictionnaire Python
documents = df.to_dict(orient="records")

