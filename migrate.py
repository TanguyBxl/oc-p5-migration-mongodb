import pandas as pd
df = pd.read_csv("data/healthcare_dataset.csv")

df.columns = df.columns.str.lower().str.strip()

for col in df.select_dtypes(include="str").columns:
    df[col] = df[col].str.strip().str.lower()

df["date of admission"] = pd.to_datetime(df["date of admission"])
df["discharge date"] = pd.to_datetime(df["discharge date"])

df = df.drop_duplicates()

df["billing amount"] = df["billing amount"].round(2)

df.columns = df.columns.str.replace(" ", "_")

documents = df.to_dict(orient="records")


from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
collection = client["healthcare_db"]["admissions"]

collection.delete_many({})
collection.insert_many(documents)

nb_docs = collection.count_documents({})
assert nb_docs == len(documents), "Erreur : le nombre de documents ne correspond pas !"
print(f"Migration réussie : {nb_docs} documents insérés.")
print(collection.find_one())

client.close()