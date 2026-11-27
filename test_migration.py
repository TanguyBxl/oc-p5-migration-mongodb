import os
from datetime import datetime
from pathlib import Path
import pytest
from pymongo import MongoClient


def load_env():
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


@pytest.fixture(scope="module")
def collection():
    load_env()
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        user = os.getenv("ETL_USERNAME", "etl_user")
        pwd = os.getenv("ETL_PASSWORD", "")
        mongo_uri = f"mongodb://{user}:{pwd}@localhost:27017/healthcare_db?authSource=healthcare_db"
    client = MongoClient(mongo_uri)
    db = client["healthcare_db"]
    yield db["admissions"]
    client.close()


# --- 1. TESTS D'INTÉGRITÉ DE LA MIGRATION ---

def test_document_count(collection):
    assert collection.count_documents({}) == 54966


def test_bson_date_types(collection):
    doc = collection.find_one()
    assert doc is not None
    assert isinstance(doc["date_of_admission"], datetime)
    assert isinstance(doc["discharge_date"], datetime)


def test_no_duplicates(collection):
    pipeline = [
        {
            "$group": {
                "_id": {
                    "name": "$name",
                    "age": "$age",
                    "gender": "$gender",
                    "blood_type": "$blood_type",
                    "medical_condition": "$medical_condition",
                    "date_of_admission": "$date_of_admission",
                    "doctor": "$doctor",
                    "hospital": "$hospital",
                    "insurance_provider": "$insurance_provider",
                    "billing_amount": "$billing_amount",
                    "room_number": "$room_number",
                    "admission_type": "$admission_type",
                    "discharge_date": "$discharge_date",
                    "medication": "$medication",
                    "test_results": "$test_results",
                },
                "count": {"$sum": 1},
            }
        },
        {"$match": {"count": {"$gt": 1}}},
    ]
    duplicates = list(collection.aggregate(pipeline))
    assert len(duplicates) == 0


def test_indexes_exist(collection):
    indexes = collection.index_information()
    assert "medical_condition_1" in indexes
    assert "date_of_admission_1" in indexes


# --- 2. TESTS CRUD AUTOMATISÉS ---

def test_crud_operations(collection):
    test_patient = {
        "name": "pytest patient",
        "age": 40,
        "gender": "male",
        "blood_type": "o+",
        "medical_condition": "asthma",
        "date_of_admission": datetime(2024, 5, 10),
        "doctor": "dr house",
        "hospital": "general hospital",
        "insurance_provider": "aetna",
        "billing_amount": 1500.00,
        "room_number": 101,
        "admission_type": "elective",
        "discharge_date": datetime(2024, 5, 12),
        "medication": "ibuprofen",
        "test_results": "normal",
    }

    # Create
    insert_res = collection.insert_one(test_patient)
    assert insert_res.inserted_id is not None

    # Read
    found = collection.find_one({"name": "pytest patient"})
    assert found is not None
    assert found["age"] == 40

    # Update
    update_res = collection.update_one(
        {"name": "pytest patient"}, {"$set": {"age": 41}}
    )
    assert update_res.modified_count == 1
    updated = collection.find_one({"name": "pytest patient"})
    assert updated["age"] == 41

    # Delete (nettoyage pour préserver les 54 966 documents)
    delete_res = collection.delete_one({"name": "pytest patient"})
    assert delete_res.deleted_count == 1
    assert collection.find_one({"name": "pytest patient"}) is None