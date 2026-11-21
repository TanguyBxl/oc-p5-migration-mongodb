# Migration de données médicales vers MongoDB

## 1. Objectif du projet
Ce projet permet de nettoyer et migrer un jeu de données hospitalières (`healthcare_dataset.csv`, 55 500 lignes) vers une base de données NoSQL MongoDB (`healthcare_db`, collection `admissions`) à l'aide de Python (`pandas` et `pymongo`).

## 2. Logique de nettoyage et règles d'intégrité
Avant l'insertion dans MongoDB, le script `migrate.py` applique les étapes suivantes :
* **Normalisation :** Passage des noms de colonnes en minuscules avec underscores (`snake_case`) et conversion de toutes les valeurs texte en minuscules (`lowercase` + `strip`) *avant* la recherche de doublons.
* **Dédoublonnage :** Suppression de **534 doublons exacts**, ce qui laisse **54 966 admissions** uniques.
* **Typage des variables :** Conversion des dates (`date_of_admission` et `discharge_date`) via `pd.to_datetime()` pour les stocker au format natif **BSON `Date`** dans MongoDB, et arrondi de `billing_amount` à 2 décimales.
* **Gestion des montants négatifs :** L'exploration (`explore.py`) a révélé **106 lignes avec un montant négatif**. Après vérification de l'historique des patients concernés, ces lignes ont été conservées car elles correspondent probablement à des remboursements ou des avoirs (en attente de confirmation du service facturation).
* **Contrôle post-migration :** Le script vide la collection avant chaque insertion (`delete_many({})`) pour éviter les doublons en cas de réexécution, puis vérifie avec `assert` que les **54 966 documents** sont bien présents en base.

## 3. Structure d'un document dans MongoDB
Chaque ligne du CSV est convertie en un document JSON plat à 15 champs dans `healthcare_db.admissions` :

```json
{
  "name": "bobby jackson",
  "age": 30,
  "gender": "male",
  "blood_type": "b-",
  "medical_condition": "cancer",
  "date_of_admission": "2024-01-31T00:00:00Z",
  "doctor": "matthew smith",
  "hospital": "sons and miller",
  "insurance_provider": "blue cross",
  "billing_amount": 18856.28,
  "room_number": 328,
  "admission_type": "urgent",
  "discharge_date": "2024-02-02T00:00:00Z",
  "medication": "paracetamol",
  "test_results": "normal"
}

# 1. Créer et activer l'environnement virtuel
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer la migration vers MongoDB
python migrate.py

# 4. Tester les opérations de base (Create, Read, Update, Delete)
python crud_test.py

## 4. Installation et exécution

### Option A : Avec Docker Compose (recommandé)
Le fichier `docker-compose.yml` orchestre deux conteneurs sur un réseau privé :
* **`mongodb` (`healthcare-mongodb`) :** base MongoDB avec stockage persistant (`volume` `mongo_data`) et contrôle de santé (`healthcheck`).
* **`migration` (`healthcare-migration`) :** image Python (`Dockerfile`) exécutant `migrate.py` via `MONGO_URI=mongodb://mongodb:27017/` dès que MongoDB est prêt.

```powershell
# 1. Construire l'image et lancer les conteneurs en arrière-plan
docker compose up --build -d

# 2. Contrôler le journal d'exécution de la migration
docker compose logs migration

# 3. Vérifier l'état des conteneurs (migration en Exited (0), mongodb en Up (healthy))
docker compose ps -a