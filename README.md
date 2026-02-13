# Banking Transactions API

[![CI/CD Pipeline](https://github.com/lucaslgk/projet_python_2_mba/actions/workflows/ci.yml/badge.svg)](https://github.com/lucaslgk/projet_python_2_mba/actions/workflows/ci.yml)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat&logo=fastapi&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.1.4-150458?style=flat&logo=pandas&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.5-E92063?style=flat&logo=pydantic&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-7.4-0A9EDC?style=flat&logo=pytest&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)
![Flake8](https://img.shields.io/badge/Flake8-PEP8-blue?style=flat)
![mypy](https://img.shields.io/badge/mypy-strict-blue?style=flat)
![NumPy](https://img.shields.io/badge/NumPy-1.26-013243?style=flat&logo=numpy&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-0.27-2D3748?style=flat&logo=gunicorn&logoColor=white)

API REST pour l'exposition et l'analyse de données de transactions bancaires, développée avec FastAPI dans le cadre du projet ESG MBA Big Data & IA.

**L'interface graphique de cette API a été développée et partagée sur le repo suivant : https://github.com/lucaslgk/banking-app-frontend**

## Table des matières

- [Présentation](#présentation)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Démarrage](#démarrage)
- [Performance et cache](#performance-et-cache)
- [Endpoints de l'API](#endpoints-de-lapi)
- [Tests](#tests)
- [Docker](#docker)
- [Application frontend](#application-frontend)
- [Structure du projet](#structure-du-projet)
- [Auteurs](#auteurs)

## Présentation

Cette application expose 20 routes API réparties en 5 catégories :

| Catégorie      | Description                              | Routes |
|----------------|------------------------------------------|--------|
| Transactions   | Consultation, filtrage, recherche        | 1 - 8  |
| Statistiques   | Agrégations globales et par critères     | 9 - 12 |
| Fraude         | Analyse et détection                     | 13 - 15|
| Clients        | Exploration des portefeuilles clients    | 16 - 18|
| Administration | Santé du service et métadonnées          | 19 - 20|

Le projet est packageé sous forme de module Python installable, testé via pytest et unittest, et intègre un pipeline CI/CD complet.

## Prérequis

- Python 3.12+
- pip
- Le fichier de données `transactions_data.csv` placé dans le répertoire `data/`

Le dataset est disponible sur Kaggle :
https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets

## Installation

### Depuis les sources

```bash
git clone https://github.com/lucaslgk/projet_python_2_mba.git
cd projet_python_2_mba

pip install -e .
```

### Avec les dépendances de développement

```bash
pip install -e ".[dev]"
```

### Via le package build

```bash
python -m build
pip install dist/banking_transactions_api-1.0.0-py3-none-any.whl
```

## Démarrage

### Lancement de l'API

```bash
uvicorn src.banking_api.app:app --host 0.0.0.0 --port 8000
```

L'API est alors accessible sur `http://localhost:8000`.

La documentation interactive Swagger est disponible sur `http://localhost:8000/docs`.

## Performance et cache

**Important :** Le dataset CSV contient un volume important de transactions. Pour optimiser les temps de chargement, l'application met en place un système de cache automatique via pickle.

**Premier lancement** : au démarrage initial, l'API lit le fichier `transactions_data.csv`, effectue le parsing des colonnes (dates, montants, types), fusionne les labels de fraude depuis `train_fraud_labels.json`, optimise les types de données (colonnes catégoriques, tri par date), puis sérialise le DataFrame résultant dans un fichier `transactions_data.pkl` dans le répertoire `data/`. **Cette opération peut prendre plusieurs dizaines de secondes selon la taille du dataset et les performances de la machine.**

**Lancements suivants** : l'application détecte automatiquement la présence du fichier `.pkl` et compare sa date de modification avec celle du CSV source. Si le cache est plus récent que le CSV, le DataFrame est chargé directement depuis le pickle, ce qui réduit le temps de démarrage à quelques secondes.

Le fichier `.pkl` est exclu du versioning Git (via `.gitignore`) et sera régénéré automatiquement à chaque modification du fichier CSV source.

En mémoire, le dataset est maintenu via un singleton (`DataLoader`) qui garantit un chargement unique et un accès partagé entre tous les services.

## Endpoints de l'API

### Transactions

| Méthode  | Endpoint                                      | Description                                  |
|----------|-----------------------------------------------|----------------------------------------------|
| GET      | `/api/transactions`                           | Liste paginée avec filtres                   |
| GET      | `/api/transactions/{id}`                      | Détails d'une transaction                    |
| POST     | `/api/transactions/search`                    | Recherche multicritère                       |
| GET      | `/api/transactions/types`                     | Types de transactions disponibles            |
| GET      | `/api/transactions/recent`                    | N dernières transactions                     |
| DELETE   | `/api/transactions/{id}`                      | Suppression (mode test)                      |
| GET      | `/api/transactions/by-customer/{customer_id}` | Transactions émises par un client            |
| GET      | `/api/transactions/to-customer/{customer_id}` | Transactions reçues par un client (voir note ci-dessous) |

**Note sur la route `to-customer`** : le dataset Kaggle utilisé dans ce projet (credit card fraud dataset) contient exclusivement des transactions de type client vers marchand. Contrairement au dataset annoncé dans le sujet qui semble inclure des transferts entre clients (champs `nameOrig` / `nameDest`), notre dataset ne comporte pas de transactions inter-clients. La route `to-customer/{customer_id}` a donc été adaptée : le paramètre `customer_id` est interprété comme un `merchant_id`, et l'endpoint retourne les transactions reçues par ce marchand. Ce choix est documenté dans le code source et permet de conserver la route fonctionnelle malgré la structure du dataset.

### Statistiques

| Méthode | Endpoint                        | Description                          |
|---------|---------------------------------|--------------------------------------|
| GET     | `/api/stats/overview`           | Statistiques globales du dataset     |
| GET     | `/api/stats/amount-distribution`| Distribution des montants            |
| GET     | `/api/stats/by-type`            | Statistiques par type de transaction |
| GET     | `/api/stats/daily`              | Volume et moyenne par jour           |

### Fraude

| Méthode | Endpoint              | Description                              |
|---------|-----------------------|------------------------------------------|
| GET     | `/api/fraud/summary`  | Vue d'ensemble de la fraude              |
| GET     | `/api/fraud/by-type`  | Taux de fraude par type de transaction   |
| POST    | `/api/fraud/predict`  | Scoring de prédiction de fraude          |

### Clients

| Méthode | Endpoint                       | Description                    |
|---------|--------------------------------|--------------------------------|
| GET     | `/api/customers`               | Liste paginée des clients      |
| GET     | `/api/customers/{customer_id}` | Profil client synthétique      |
| GET     | `/api/customers/top`           | Top clients par volume         |

### Administration

| Méthode | Endpoint               | Description                     |
|---------|------------------------|---------------------------------|
| GET     | `/api/system/health`   | État de santé de l'API          |
| GET     | `/api/system/metadata` | Version et métadonnées          |

## Tests

### Lancer les tests unitaires (pytest)

```bash
pytest
```

### Lancer les tests avec couverture

```bash
pytest --cov=src/banking_api --cov-report=term-missing --cov-report=html
```

Le rapport HTML est généré dans le répertoire `htmlcov/`.

### Lancer les tests features (unittest)

```bash
python -m unittest discover tests/features
```

### Vérification du code

```bash
flake8 src tests
mypy src
```

## Docker

### Construction et lancement via Docker Compose

```bash
docker-compose up --build
```

### Construction manuelle de l'image

```bash
docker build -t banking-transactions-api .
docker run -p 8000:8000 -v ./data:/app/data:ro banking-transactions-api
```

## Application frontend

Une interface web accompagne cette API. Elle est développée dans un projet séparé avec le framework [Reflex](https://reflex.dev) (Python) et communique avec l'ensemble des endpoints décrits ci-dessus via un client HTTP asynchrone (`httpx`).

L'application propose quatre pages :

| Page          | Description                                                  |
|---------------|--------------------------------------------------------------|
| Dashboard     | Vue d'ensemble des statistiques, transactions récentes et état du système |
| Transactions  | Historique complet avec filtres avancés et recherche multicritère |
| Clients       | Top clients par volume et consultation de profils individuels |
| Fraude        | Synthèse des indicateurs de fraude et formulaire de prédiction |

Le frontend nécessite que l'API backend soit accessible sur `http://localhost:8000`. Le code source et les instructions de démarrage sont disponibles dans le repository dédié :
https://github.com/lucaslgk/banking-app-frontend

## Structure du projet

```
projet_python_2_mba/
├── src/
│   └── banking_api/
│       ├── __init__.py
│       ├── app.py                  # Application FastAPI
│       ├── routes/
│       │   ├── transactions.py     # Routes transactions
│       │   ├── stats.py            # Routes statistiques
│       │   ├── fraud.py            # Routes fraude
│       │   ├── customers.py        # Routes clients
│       │   └── system.py           # Routes administration
│       ├── services/
│       │   ├── transactions_service.py
│       │   ├── stats_service.py
│       │   ├── fraud_detection_service.py
│       │   ├── customer_service.py
│       │   └── system_service.py
│       ├── models/
│       │   ├── transaction.py      # Modèles Pydantic transactions
│       │   ├── stats.py            # Modèles statistiques
│       │   ├── customer.py         # Modèles clients
│       │   └── system.py           # Modèles système
│       └── utils/
│           └── data_loader.py      # Chargement et cache du dataset
├── tests/
│   ├── conftest.py                 # Fixtures pytest
│   ├── unit/                       # Tests unitaires (pytest)
│   │   ├── test_transactions_routes.py
│   │   ├── test_stats_routes.py
│   │   ├── test_fraud_routes.py
│   │   ├── test_customer_routes.py
│   │   ├── test_system_routes.py
│   │   ├── test_services.py
│   │   └── test_transactions_service_extras.py
│   └── features/                   # Tests features (unittest)
│       └── test_api_features.py
├── data/                           # Données (non versionné)
├── .github/
│   └── workflows/
│       └── ci.yml                  # Pipeline CI/CD
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── setup.py
├── MANIFEST.in
└── README.md
```

## Auteurs

- Lucas Goumard
- Ines Taibi
- Aghilas Aissaoui
- Myriam Bennani

Projet réalisé dans le cadre du MBA ESG Big Data & IA — Programmation en Python
