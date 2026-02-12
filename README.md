# Banking Transactions API

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📋 Description

API REST complète pour l'exposition et la manipulation des données de transactions bancaires. Ce projet fait partie du programme MBA 2 - Python de l'ESG.

L'API permet de :
- ✅ Consulter, rechercher et filtrer des transactions bancaires
- 📊 Obtenir des statistiques agrégées et analytiques
- 🔍 Analyser et détecter la fraude
- 👥 Explorer les portefeuilles clients
- 🏥 Superviser l'état du service

## 🚀 Fonctionnalités

### 20 Endpoints API

| Catégorie | Endpoints | Description |
|-----------|-----------|-------------|
| **Transactions** | 8 routes | Consultation, filtrage, recherche, suppression |
| **Statistiques** | 4 routes | Agrégations globales et par critères |
| **Fraude** | 3 routes | Analyse et détection de fraude |
| **Clients** | 3 routes | Exploration des portefeuilles clients |
| **Administration** | 2 routes | Métadonnées & supervision du service |

## 📦 Installation

### Prérequis

- Python 3.12 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation depuis les sources

```powershell
# Cloner le repository
git clone <votre-repo-url>
cd "Projet FastAPI"

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Ou installer en mode développement
pip install -e .
```

### Installation des dépendances de développement

```powershell
pip install -r requirements-dev.txt
```

## 🏃 Utilisation

### Démarrer l'API

```powershell
# Méthode 1: Utiliser uvicorn directement
uvicorn banking_api.main:app --reload

# Méthode 2: Utiliser le script d'entrée
python -m banking_api.main

# Méthode 3: Si installé comme package
banking-api
```

L'API sera accessible à l'adresse : `http://localhost:8000`

### Documentation interactive

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

## 📊 Données

Les données doivent être placées dans le dossier `data/` :

```
data/
└── transactions_data.csv    # Données de transactions (requis)
```

**Note:** Seules les données de transactions sont nécessaires. L'API utilise directement les colonnes du fichier CSV pour toutes ses opérations.

Source des données : [Kaggle - Transactions Fraud Datasets](https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets)

## 🧪 Tests

### Tests avec pytest (tests unitaires)

```powershell
# Exécuter tous les tests
pytest

# Avec couverture de code
pytest --cov=banking_api --cov-report=html

# Tests spécifiques
pytest tests/unit/test_transactions_routes.py
```

### Tests avec unittest (tests de features)

```powershell
# Exécuter tous les tests unittest
python -m unittest discover tests/features

# Test spécifique
python -m unittest tests.features.test_transactions_features
```

### Couverture de code

Le projet vise une couverture de code ≥ 85%

```powershell
# Générer le rapport de couverture
pytest --cov=banking_api --cov-report=term-missing --cov-report=html

# Ouvrir le rapport HTML
start htmlcov/index.html
```

## 🔍 Qualité du code

### Linting avec flake8

```powershell
# Vérifier la conformité PEP8
flake8 banking_api/

# Vérifier tout le projet
flake8 .
```

### Vérification des types avec mypy

```powershell
# Vérifier le typage
mypy banking_api/
```


## 📦 Construction du package

### Avec le script PowerShell (recommandé)

```powershell
# Construire le package
.\build.ps1
```

### Avec setuptools

```powershell
# Installer build
pip install build

# Construire le package
python -m build

# Les fichiers seront dans dist/
```

### Avec poetry (optionnel)

```powershell
# Installer poetry
pip install poetry

# Construire
poetry build
```

## 📁 Structure du projet

```
Projet FastAPI/
├── banking_api/                # Code source principal
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── models/                 # Modèles Pydantic
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routes/                 # Endpoints API
│   │   ├── __init__.py
│   │   ├── transactions.py
│   │   ├── statistics.py
│   │   ├── fraud.py
│   │   ├── customers.py
│   │   └── system.py
│   └── services/               # Logique métier
│       ├── __init__.py
│       ├── data_loader.py
│       ├── transactions_service.py
│       ├── stats_service.py
│       ├── fraud_detection_service.py
│       ├── customer_service.py
│       └── system_service.py
├── tests/                      # Tests
│   ├── unit/                   # Tests pytest
│   │   ├── test_transactions_routes.py
│   │   ├── test_statistics_routes.py
│   │   ├── test_fraud_routes.py
│   │   ├── test_customers_routes.py
│   │   └── test_system_routes.py
│   └── features/               # Tests unittest
│       ├── test_transactions_features.py
│       ├── test_statistics_features.py
│       ├── test_fraud_features.py
│       ├── test_customers_features.py
│       └── test_system_features.py
├── data/                       # Données (CSV)
│   └── transactions_data.csv
├── pyproject.toml              # Configuration du projet
├── setup.py                    # Setup setuptools
├── requirements.txt            # Dépendances
├── requirements-dev.txt        # Dépendances dev
├── .flake8                     # Configuration flake8
├── mypy.ini                    # Configuration mypy
├── .gitignore                  # Fichiers ignorés par git
└── README.md                   # Ce fichier
```

## 🔗 Endpoints API

### Transactions (8 endpoints)

- `GET /api/transactions` - Liste paginée avec filtres
- `GET /api/transactions/{id}` - Détails d'une transaction
- `POST /api/transactions/search` - Recherche multicritère
- `GET /api/transactions/types` - Types disponibles
- `GET /api/transactions/recent` - Dernières transactions
- `DELETE /api/transactions/{id}` - Suppression (test)
- `GET /api/transactions/by-customer/{customer_id}` - Transactions d'un client
- `GET /api/transactions/to-customer/{customer_id}` - Transactions reçues

### Statistiques (4 endpoints)

- `GET /api/stats/overview` - Vue d'ensemble
- `GET /api/stats/amount-distribution` - Distribution des montants
- `GET /api/stats/by-type` - Stats par type
- `GET /api/stats/daily` - Stats quotidiennes

### Fraude (3 endpoints)

- `GET /api/fraud/summary` - Résumé de la fraude
- `GET /api/fraud/by-type` - Fraude par type
- `POST /api/fraud/predict` - Prédiction de fraude

### Clients (3 endpoints)

- `GET /api/customers` - Liste paginée
- `GET /api/customers/{customer_id}` - Profil client
- `GET /api/customers/top` - Top clients

### Système (2 endpoints)

- `GET /api/system/health` - État de santé
- `GET /api/system/metadata` - Métadonnées

## 👥 Équipe

Projet réalisé dans le cadre du MBA 2 - Python - ESG

## 📄 Licence

MIT License - voir le fichier LICENSE pour plus de détails

## 📚 Documentation supplémentaire

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

---
