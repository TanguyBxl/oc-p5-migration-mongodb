# Migration de données médicales vers MongoDB (Docker & Python)

Pipeline ETL conteneurisé permettant de nettoyer, typifier et migrer un jeu de données hospitalières (CSV) vers **MongoDB**, avec gestion des accès par rôles (RBAC) et suite de tests automatisés.

## Architecture du projet

* **`migrate.py`** : Script ETL Python (`pandas`, `pymongo`) assurant la normalisation des chaînes, la conversion des dates au format BSON `ISODate`, le dédoublonnage strict (54 966 enregistrements uniques conservés), l'insertion en base et la création des index.
* **`Dockerfile` & `docker-compose.yml`** : Orchestration de deux services isolés sur le réseau bridge `healthcare_net` :
  * `healthcare-mongodb` (`mongo:latest`) avec volume persistant (`mongo_data`) et `healthcheck` authentifié.
  * `healthcare-migration` (`python:3.12-slim`) exécutant la migration dès que MongoDB est opérationnel.
* **`mongo-init.js`** : Script d'initialisation créant deux utilisateurs dédiés sur `healthcare_db` selon le principe du moindre privilège :
  * `etl_user` : rôle `readWrite` (utilisé par le pipeline ETL et les tests).
  * `analyst_user` : rôle `read` (accès analytique en lecture seule).
* **`test_migration.py`** : Suite de 5 tests automatisés avec `pytest` validant l'intégrité des données et le cycle CRUD.
* **`.env.example`** : Modèle des variables d'environnement requises (les identifiants réels sont stockés dans `.env`, ignoré par Git).

## Structure du dépôt

```text
├── data/                  # Dossier local pour le fichier CSV source (ignoré par Git)
├── .env.example           # Modèle de configuration des identifiants
├── .gitignore             # Exclusion des secrets (.env), données (.csv) et caches
├── docker-compose.yml     # Orchestration des conteneurs, réseau et volume
├── Dockerfile             # Image du service de migration Python
├── migrate.py             # Script ETL et création des index
├── mongo-init.js          # Création des utilisateurs RBAC MongoDB
├── README.md              # Documentation du projet
├── requirements.txt       # Dépendances Python
└── test_migration.py      # Tests d'intégrité et CRUD (pytest)