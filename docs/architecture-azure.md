# Étude d'architecture Cloud : Migration vers Microsoft Azure

## Contexte
À l'issue de l'étape 2, le pipeline ETL (`migrate.py`) et la base MongoDB (`healthcare_db.admissions`, **54 966 documents**) sont conteneurisés et orchestrés localement via **Docker Compose**. Cette étude présente l'architecture cible sur **Microsoft Azure** pour industrialiser ce flux en production, sans réécrire le code métier Python.

---

## 1. Bénéfices métier du passage au Cloud pour le client
* **Haute disponibilité (SLA 99,99 %+) :** Réplication automatique des données sur plusieurs zones de disponibilité, éliminant le point de défaillance unique d'un serveur local.
* **Scalabilité élastique :** Absorption transparente de la montée en charge (passage de 55 000 à plusieurs millions d'admissions) sans intervention matérielle.
* **Sécurité et conformité médicale :** Chiffrement natif au repos (AES-256) et en transit (TLS 1.2+), contrôle d'accès par rôle (RBAC) et conformité aux normes de santé (**HIPAA**, **ISO 27001**, **HDS**).
* **Délégation de la maintenance (PaaS) :** Sauvegardes automatisées, restauration à un instant T (*Point-in-Time Restore*) et mises à jour de sécurité gérées par Azure.

---

## 2. Architecture cible sur Microsoft Azure

```text
[Azure Blob Storage] (healthcare_dataset.csv)
         │
         ▼ (Lecture sécurisée)
[Azure Container Apps Job] ◄── [Azure Container Registry (ACR)] (Image Docker)
         │
         ├──► [Azure Key Vault] (Récupération du secret MONGO_URI)
         │
         ▼ (Insertion via Private Endpoint)
[Azure Cosmos DB for MongoDB] (Base managées : healthcare_db.admissions)