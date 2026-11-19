import os
import pandas as pd
from pymongo import MongoClient, ASCENDING

CSV_PATH = "data/healthcare_dataset.csv"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "healthcare_db"
COLLECTION_NAME = "admissions"


def extract_and_clean(csv_path: str) -> pd.DataFrame:
    """Charge le CSV, supprime les doublons et normalise les types."""
    df = pd.read_csv(csv_path)
    initial_count = len(df)

    # 1. Suppression des doublons exacts
    df = df.drop_duplicates().copy()
    print(f"[CLEAN] Lignes initiales : {initial_count} | Doublons supprimés : {initial_count - len(df)}")

    # 2. Normalisation des chaînes de caractères
    df["Name"] = df["Name"].str.strip().str.title()
    for col in ["Gender", "Blood Type", "Medical Condition", "Doctor", "Hospital", "Insurance Provider", "Admission Type", "Medication", "Test Results"]:
        df[col] = df[col].str.strip()

    # 3. Typage des dates et arrondi financier
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"])
    df["Billing Amount"] = df["Billing Amount"].round(2)

    return df


def transform_to_documents(df: pd.DataFrame) -> list[dict]:
    """Transforme chaque ligne nettoyée en document JSON structuré pour MongoDB."""
    documents = []
    for row in df.itertuples(index=False):
        doc = {
            "patient": {
                "name": row.Name,
                "age": int(row.Age),
                "gender": row.Gender,
                "blood_type": row._3,  # Blood Type
            },
            "medical": {
                "condition": row._4,   # Medical Condition
                "medication": row.Medication,
                "test_results": row._14,  # Test Results
            },
            "hospitalization": {
                "hospital": row.Hospital,
                "doctor": row.Doctor,
                "room_number": int(row._10),  # Room Number
                "admission_type": row._11,    # Admission Type
                "admission_date": row._5.to_pydatetime(),   # Date of Admission
                "discharge_date": row._12.to_pydatetime(),  # Discharge Date
            },
            "billing": {
                "insurance_provider": row._8,  # Insurance Provider
                "amount": float(row._9),       # Billing Amount
            },
        }
        documents.append(doc)
    return documents


def load_to_mongodb(documents: list[dict]) -> None:
    """Insère les documents dans MongoDB, crée les index et vérifie l'intégrité."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Idempotence : purge avant rechargement complet
    collection.delete_many({})

    # Insertion en lot (bulk insert)
    result = collection.insert_many(documents)
    inserted_count = len(result.inserted_ids)

    # Création des index de performance
    collection.create_index([("patient.name", ASCENDING)])
    collection.create_index([("medical.condition", ASCENDING)])
    collection.create_index([("hospitalization.admission_date", ASCENDING)])

    # Contrôle d'intégrité post-migration
    db_count = collection.count_documents({})
    assert db_count == len(documents), f"Erreur d'intégrité : {db_count} != {len(documents)}"

    print(f"[LOAD] {inserted_count} documents insérés avec succès dans '{DB_NAME}.{COLLECTION_NAME}'.")
    print(f"[CHECK] Intégrité validée : {db_count} documents présents en base.")
    client.close()


if __name__ == "__main__":
    clean_df = extract_and_clean(CSV_PATH)
    docs = transform_to_documents(clean_df)
    load_to_mongodb(docs)

