# Banking Transactions API

API REST complète pour l'exposition et la manipulation des données de transactions bancaires.

## Description

Cette API FastAPI permet de :
- Consulter, rechercher et filtrer des transactions bancaires
- Obtenir des statistiques agrégées et analytiques
- Analyser la fraude et la détection
- Explorer les portefeuilles clients
- Superviser le service via des endpoints d'administration

## Installation

### Prérequis
- Python 3.12+
- pip

### Installation du package

```bash
# Cloner le repository
git clone https://github.com/yourusername/banking-transactions-api.git
cd banking-transactions-api

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Ou installer le package en mode développement
pip install -e ".[dev]"
```

## 📊 Données

Téléchargez le dataset depuis Kaggle :
https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets/data

Placez le fichier `transactions_data.csv` dans le dossier `app/data/`.

## Lancement

```bash
# Lancement direct
uvicorn app.main:app --reload

# Ou via le script d'entrée
banking-api
```

L'API sera accessible sur : http://localhost:8000

Documentation interactive : http://localhost:8000/docs

## Tests

```bash
# Lancer tous les tests avec couverture
pytest

# Tests unitaires uniquement
pytest tests/unit/

# Tests features uniquement
python -m unittest discover tests/features/

# Avec rapport de couverture détaillé
pytest --cov=app --cov-report=html
```

## Qualité du code

```bash
# Vérification PEP8
flake8 app/

# Vérification du typing
mypy app/

# Formatage du code
black app/
```

## 📦 Build du package

```bash
# Avec setuptools
python setup.py sdist bdist_wheel

# Avec build
python -m build
```

## Documentation API

### Routes principales (20 endpoints)

#### Transactions (8 routes)
1. `GET /api/transactions` - Liste paginée
2. `GET /api/transactions/{id}` - Détails d'une transaction
3. `POST /api/transactions/search` - Recherche multicritère
4. `GET /api/transactions/types` - Types disponibles
5. `GET /api/transactions/recent` - Transactions récentes
6. `DELETE /api/transactions/{id}` - Suppression
7. `GET /api/transactions/by-customer/{customer_id}` - Par client origine
8. `GET /api/transactions/to-customer/{customer_id}` - Par client destination

#### Statistiques (4 routes)
9. `GET /api/stats/overview` - Vue d'ensemble
10. `GET /api/stats/amount-distribution` - Distribution des montants
11. `GET /api/stats/by-type` - Stats par type
12. `GET /api/stats/daily` - Stats quotidiennes

#### Fraude (3 routes)
13. `GET /api/fraud/summary` - Résumé fraude
14. `GET /api/fraud/by-type` - Fraude par type
15. `POST /api/fraud/predict` - Prédiction

#### Clients (3 routes)
16. `GET /api/customers` - Liste clients
17. `GET /api/customers/{customer_id}` - Profil client
18. `GET /api/customers/top` - Top clients

#### Système (2 routes)
19. `GET /api/system/health` - Santé
20. `GET /api/system/metadata` - Métadonnées

##  Structure du Projet

```
banking-transactions-api/
├── app/
│   ├── api/                  # Routes API (20 endpoints)
│   │   ├── transactions.py   # 8 routes
│   │   ├── stats.py          # 4 routes
│   │   ├── fraud.py          # 3 routes
│   │   ├── customers.py      # 3 routes
│   │   └── system.py         # 2 routes
│   ├── models/               # Modèles Pydantic
│   │   └── schemas.py        # 18 modèles
│   ├── services/             # Logique métier
│   │   ├── transactions_service.py
│   │   ├── stats_service.py
│   │   ├── fraud_detection_service.py
│   │   ├── customer_service.py
│   │   └── system_service.py
│   ├── utils/                # Utilitaires
│   │   └── loader.py         # Chargement des données
│   ├── data/                 # Données
│   │   └── transactions_data.csv
│   └── main.py               # Point d'entrée
├── tests/                    # Tests
│   ├── unit/                 # Tests PyTest
│   └── features/             # Tests Unittest
├── setup.py                  # Configuration setuptools
├── pyproject.toml            # Configuration moderne
├── requirements.txt          # Dépendances prod
├── requirements-dev.txt      # Dépendances dev
├── pytest.ini                # Config pytest
├── .flake8                   # Config linter
├── mypy.ini                  # Config typing
└── README.md                 # Ce fichier
```

## Technologies Utilisées

- **Python**: 3.12+
- **Framework**: FastAPI 0.109.0
- **Validation**: Pydantic 2.5.3
- **Data Processing**: Pandas 2.2.0
- **Testing**: pytest 7.4.4, unittest
- **Quality**: flake8, mypy, black

## Statistiques du Projet

- **Lignes de code**: 3000+
- **Fichiers Python**: 30+
- **Routes API**: 20
- **Services métier**: 5
- **Modèles Pydantic**: 18
- **Tests**: 60+
- **Couverture**: ≥80%

## Auteurs
FALL Magueye
DRANÉ-COPHY Thandie
DUFERMEAU Jephté
GNANVI Emeric

MBA2 - Python - ESG
Pour lancer l'appliactaion : python -m uvicorn app.main:app --reload