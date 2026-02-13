# Banking Transactions API - Projet Python MBA

API REST complète pour l'exposition et la manipulation des données de transactions bancaires fictives.

## Description

Ce projet a été développé dans le cadre du cours de Python MBA. L'API permet de :
- Consulter, rechercher et filtrer les transactions bancaires
- Obtenir des statistiques agrégées et analytiques
- Analyser les transactions frauduleuses
- Explorer les portefeuilles clients
- Superviser l'état du service

## Technologies utilisées

- **Python 3.12+**
- **FastAPI** - Framework web moderne
- **Pandas** - Manipulation de données
- **Pytest** - Tests unitaires
- **Unittest** - Tests complémentaires

## Installation

### Prérequis
- Python 3.12 ou supérieur
- Git

### Installation du package (Recommandé)

Le projet est packagé comme un module Python installable. Cela permet de lancer l'API avec une simple commande.

```bash
# Cloner le repository
git clone https://github.com/seynabou2/projet_python_2_mba.git
cd projet_python_2_mba

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows PowerShell :
venv\Scripts\Activate.ps1
# Windows CMD :
venv\Scripts\activate.bat
# Linux/Mac :
source venv/bin/activate

# Installer le package en mode développement avec les dépendances de dev
pip install -e ".[dev]"
```

**Avantages de `pip install -e .` :**
-  Installation en mode éditable (les modifications de code sont immédiatement prises en compte)
- Commande `banking-api` disponible pour lancer l'API facilement
- Le package est accessible depuis n'importe où dans l'environnement virtuel

### Installation alternative (dépendances uniquement)

Si vous préférez ne pas installer le package :

```bash
# Installer les dépendances de production
pip install -r requirements.txt

# Pour le développement (tests, linting)
pip install -r requirements-dev.txt
```

## Données

**Important** : Le fichier CSV des transactions n'est pas inclus dans ce repository (conformément aux consignes du projet).

Pour utiliser l'API, téléchargez le dataset depuis :
https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets/

Placez le fichier dans un dossier `data/` à la racine du projet.

## Utilisation

### Lancer l'API

Après installation avec `pip install -e .`, vous pouvez lancer l'API de trois façons :

#### Méthode 1 : Commande directe (Recommandé)
```bash
banking-api
```

#### Méthode 2 : Module Python
```bash
python -m banking_api.main
```

#### Méthode 3 : Uvicorn direct
```bash
uvicorn banking_api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur : **http://localhost:8000**

### Accéder à la documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Routes disponibles

### Transactions (8 routes)
- `GET /api/transactions` - Liste paginée des transactions
- `GET /api/transactions/{id}` - Détails d'une transaction
- `POST /api/transactions/search` - Recherche multicritère
- `GET /api/transactions/types` - Types de transactions disponibles
- `GET /api/transactions/recent` - Dernières transactions
- `DELETE /api/transactions/{id}` - Suppression (mode test)
- `GET /api/transactions/by-customer/{customer_id}` - Transactions émises par un client
- `GET /api/transactions/to-customer/{customer_id}` - Transactions reçues par un client

### Statistiques (4 routes)
- `GET /api/stats/overview` - Vue d'ensemble statistique
- `GET /api/stats/amount-distribution` - Distribution des montants
- `GET /api/stats/by-type` - Statistiques par type de transaction
- `GET /api/stats/daily` - Évolution quotidienne des transactions

### Détection de fraude (3 routes)
- `GET /api/fraud/summary` - Résumé des fraudes détectées
- `GET /api/fraud/by-type` - Analyse de fraude par type
- `POST /api/fraud/predict` - Prédiction de fraude pour une transaction

### Clients (3 routes)
- `GET /api/customers` - Liste des clients
- `GET /api/customers/{customer_id}` - Profil détaillé d'un client
- `GET /api/customers/top` - Top clients par volume de transactions

### Administration (2 routes)
- `GET /api/system/health` - État de santé du système
- `GET /api/system/metadata` - Métadonnées du service

## Tests

```bash
# Lancer tous les tests avec pytest
pytest

# Tests avec rapport de couverture
pytest --cov=banking_api --cov-report=html

# Tests unitaires avec unittest
python -m unittest discover tests
```

### Vérification de la qualité du code

#### Installation des outils de formatage (optionnel)
```bash
pip install black isort
```

#### Vérifications de base
```bash
# Vérifier uniquement le module banking_api
flake8 banking_api
mypy banking_api

# Vérifier le module tests
flake8 tests
mypy tests
```

#### Vérifications de formatage PEP8
```bash
# Vérifier le formatage avec black (mode check seulement)
black --check banking_api/

# Vérifier l'ordre des imports
isort --check-only banking_api/

# Vérifier tout le projet
black --check .
isort --check-only .
```

**Note importante** : 
- `flake8 banking_api` et `mypy banking_api` vérifient uniquement le code source de l'API
- `flake8 .` et `mypy .` vérifient **tout** le projet, y compris les tests, setup.py, etc.
- Il est recommandé d'utiliser les commandes avec `.` pour une vérification complète
- `black --check` et `isort --check-only` ne modifient pas les fichiers, ils vérifient seulement
- `black` et `isort` sans `--check` modifient automatiquement les fichiers

### Couverture des tests

Le projet vise une couverture de tests supérieure à 90%.

## Structure du projet
```
projet_python_2_mba/
├── banking_api/              # Code source de l'API
│   ├── __init__.py
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration
│   ├── models/              # Modèles Pydantic
│   ├── routes/              # Routes de l'API
│   ├── services/            # Logique métier
│   └── utils/               # Utilitaires
├── tests/                    # Tests unitaires
│   ├── test_routes.py
│   └── test_services.py
├── .github/                  # CI/CD workflows (bonus)
├── data/                     # Données CSV (non versionné)
├── requirements.txt          # Dépendances production
├── requirements-dev.txt      # Dépendances développement
├── setup.py                  # Configuration du package
├── pyproject.toml           # Configuration des outils
├── pytest.ini               # Configuration pytest
├── mypy.ini                 # Configuration mypy
├── .flake8                  # Configuration flake8
├── .gitignore               # Fichiers ignorés par Git
├── Dockerfile               # Conteneurisation
└── README.md                # Ce fichier
```

## Docker (optionnel)

```bash
# Construire l'image
docker build -t banking-api .

# Lancer le conteneur
docker run -p 8000:8000 banking-api
```

## Application Streamlit (Bonus)

Une application de visualisation interactive a été développée pour explorer les données de l'API.

**Repository** : https://github.com/seynabou2/banking_api_streamlit_app

**Fonctionnalités :**
- Visualisation des transactions en temps réel
- Graphiques et statistiques interactives
- Analyse de la détection de fraude
- Dashboard des clients et métriques

**Pour utiliser l'application Streamlit :**
1. Cloner le repository séparé
2. Installer les dépendances
3. Lancer l'API Banking (ce projet sur le port 8000)
4. Lancer l'application Streamlit

## Fonctionnalités bonus

- CI/CD avec GitHub Actions
- Couverture de tests > 90%
- Type checking avec mypy
- Linting avec flake8
- Conteneurisation Docker
- Application Streamlit de visualisation
- Package Python installable

## Contributeurs

- SENE Seynabou
- NDIAYE Mame Diarra
- KODIA Mathis

## Ressources

- [Sujet du projet](projet_python.pdf)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Dataset Kaggle](https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets/)
- [Application Streamlit](https://github.com/seynabou2/banking_api_streamlit_app)

---

**Projet réalisé dans le cadre du MBA en Big Data et Intelligence Artificielle**
