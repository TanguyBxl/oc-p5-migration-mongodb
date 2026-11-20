from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
collection = client["healthcare_db"]["admissions"]

#CREATE un nouveau patient
collection.insert_one({"name": "test patient", "age": 40, "medical_condition": "asthma"})

## READ le patient
patient = collection.find_one({"name": "test patient"})
print("Avant update :", patient)

patients_cancer = list(collection.find({"medical_condition": "cancer"}).limit(3))
print("Patients cancer récupérés :", len(patients_cancer))

# UPDATE le patient
collection.update_one({"name": "test patient"}, {"$set": {"age": 41}})
print("Après update :", collection.find_one({"name": "test patient"}))

# DELETE le patient
collection.delete_one({"name": "test patient"})
print("Après delete :", collection.find_one({"name": "test patient"}))

client.close()