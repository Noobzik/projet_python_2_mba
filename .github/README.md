# 🏦 Banking Transactions API

##  Application Web Streamlit

Interface web métier développée séparément.

📦 **Repository Streamlit** : [banking-api-streamlit](https://github.com/payebie/banking-api-streamlit)

<div align="center">

![Tests](https://github.com/CamilleThauvin/projet_python_2_mba/workflows/Tests/badge.svg)
![Linting](https://github.com/CamilleThauvin/projet_python_2_mba/workflows/Linting/badge.svg)
![Deploy](https://github.com/CamilleThauvin/projet_python_2_mba/workflows/Deploy/badge.svg)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.2.0-150458.svg)
![Code Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Une API REST moderne et performante pour l'analyse de transactions bancaires**

[Documentation API](#-documentation-api) •
[Installation](#-installation) •
[Utilisation](#-utilisation) •
[Architecture](#-architecture) •
[Tests](#-tests)

</div>

---

## 📋 Table des matières

- [À propos](#-à-propos)
- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Documentation API](#-documentation-api)
- [Architecture](#-architecture)
- [Tests](#-tests)
- [Optimisations](#-optimisations)
- [Qualité du code](#-qualité-du-code)
- [CI/CD](#-cicd)
- [Contribution](#-contribution)

---

## 🎯 À propos

Cette API REST permet d'exposer et d'analyser un large volume de transactions bancaires fictives. Le projet a été développé dans le cadre d'un MBA en Data Science et met l'accent sur les bonnes pratiques de développement, la performance et la qualité du code.

### 📊 Chiffres clés

- **13+ millions** de transactions analysées
- **86%** de couverture de tests
- **< 100ms** temps de réponse moyen (avec cache)
- **100%** conformité PEP8

---

## ✨ Fonctionnalités

### 🔍 Gestion des transactions
- Recherche avancée de transactions (montant, date, type, merchant)
- Récupération des transactions récentes avec pagination
- Filtrage par client ou commerçant
- Détails complets d'une transaction

### 👥 Gestion des clients
- Liste paginée des clients
- Profil détaillé par client
- Top clients par volume de transactions
- Analyse du comportement client

### 📈 Statistiques et analyses
- Vue d'ensemble des transactions
- Statistiques par type de paiement (Chip, Swipe, Online)
- Tendances quotidiennes sur N jours
- Distribution des montants par tranches
- Analyse géographique (par ville, état, code postal)

### 🚨 Détection de fraude
- Résumé global de la fraude
- Taux de fraude par type de transaction
- Identification des transactions frauduleuses
- Métriques de précision et recall

---

## 🛠 Technologies

### Backend & Framework
- **Python 3.11+** - Langage de programmation
- **FastAPI 0.128.0** - Framework web moderne et performant
- **Uvicorn** - Serveur ASGI haute performance
- **Pydantic** - Validation des données

### Traitement de données
- **Pandas 2.2.0** - Manipulation et analyse de données
- **NumPy** - Calculs numériques
- **LRU Cache** - Mise en cache pour optimisation

### Tests & Qualité
- **Pytest 9.0.2** - Framework de tests
- **Pytest-cov 7.0.0** - Couverture de code
- **Flake8 7.3.0** - Linting et conformité PEP8
- **Black 25.1.0** - Formatage automatique du code
- **isort 6.0.0** - Organisation des imports
- **mypy 1.17.0** - Vérification de types statiques

### DevOps & CI/CD
- **GitHub Actions** - Intégration continue
- **Docker** - Containerisation
- **Git** - Gestion de versions

---

## 📦 Prérequis

- **Python** 3.11 ou supérieur
- **pip** pour la gestion des dépendances
- **Git** pour le clonage du projet
- (Optionnel) **Docker** pour la containerisation

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/CamilleThauvin/projet_python_2_mba.git
cd projet_python_2_mba
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
# Dépendances principales
pip install -r requirements.txt

# Dépendances de développement (optionnel)
pip install -r requirements-dev.txt
```

### 4. Préparer les données

Placez vos fichiers de données dans le dossier `data/` :
- `transactions_data.csv` - Dataset complet
- `transactions_sample.csv` - Dataset réduit pour tests
- `fraud_labels.csv` - Labels de fraude

**Important :** Les fichiers CSV ne sont pas inclus dans le dépôt Git.

---

## 💻 Utilisation

### Démarrer le serveur

```bash
uvicorn banking_api.main:app --reload
```

Le serveur démarre sur `http://localhost:8000`

### Accéder à la documentation interactive

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Exemple de requêtes

```bash
# Récupérer les statistiques globales
curl http://localhost:8000/api/stats/overview

# Lister les clients avec pagination
curl http://localhost:8000/api/customers?skip=0&limit=50

# Rechercher des transactions
curl -X POST http://localhost:8000/api/transactions/search \
  -H "Content-Type: application/json" \
  -d '{"min_amount": 100, "max_amount": 1000}'

# Obtenir le résumé de fraude
curl http://localhost:8000/api/fraud/summary
```

---

## 📖 Documentation API

### Endpoints principaux

#### 🔄 Transactions

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/transactions/recent` | Transactions récentes (avec pagination) |
| POST | `/api/transactions/search` | Recherche avancée |
| GET | `/api/transactions/{id}` | Détails d'une transaction |
| GET | `/api/transactions/by-customer/{id}` | Transactions d'un client |

#### 👤 Clients

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/customers` | Liste paginée des clients |
| GET | `/api/customers/{id}` | Profil d'un client |
| GET | `/api/customers/top` | Top clients |

#### 📊 Statistiques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/stats/overview` | Vue d'ensemble |
| GET | `/api/stats/by-type` | Stats par type de paiement |
| GET | `/api/stats/daily` | Tendances quotidiennes |
| GET | `/api/stats/amount-distribution` | Distribution des montants |

#### 🚨 Fraude

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/fraud/summary` | Résumé global |
| GET | `/api/fraud/by-type` | Fraude par type de transaction |

### Modèles de données

#### Transaction
```json
{
  "id": "123456",
  "date": "2023-01-15 14:30:00",
  "client_id": 100,
  "card_id": 200,
  "amount": 45.50,
  "use_chip": "Chip Transaction",
  "merchant_id": 5000,
  "merchant_city": "Paris",
  "merchant_state": "IDF",
  "zip": "75001",
  "mcc": "5411",
  "errors": "",
  "isFraud": 0
}
```

#### Customer Profile
```json
{
  "id": "100",
  "transaction_count": 245,
  "avg_amount": 67.32,
  "fraud_count": 3,
  "fraudulent": true
}
```

---

## 🏗 Architecture

### Structure du projet

```
projet_python_2_mba/
├── banking_api/               # Code source principal
│   ├── __init__.py
│   ├── main.py               # Point d'entrée FastAPI
│   ├── routes/               # Endpoints API
│   │   ├── customers.py      # Routes clients (avec pagination)
│   │   ├── fraud.py          # Routes détection fraude
│   │   ├── stats.py          # Routes statistiques
│   │   └── transactions.py   # Routes transactions
│   └── services/             # Logique métier
│       ├── data_cache.py     # Cache LRU pour performances
│       ├── fraud_labels_loader.py
│       └── ...
├── tests/                    # Tests unitaires et d'intégration
│   ├── test_services.py
│   ├── test_fraud.py
│   └── fixtures/
├── data/                     # Données (non versionnées)
├── .github/workflows/        # CI/CD GitHub Actions
├── requirements.txt          # Dépendances production
├── requirements-dev.txt      # Dépendances développement
└── README.md                # Cette documentation
```

### Patterns et bonnes pratiques

- **Architecture en couches** : Séparation routes/services
- **Dependency Injection** : Utilisation des dépendances FastAPI
- **Caching stratégique** : LRU cache pour données fréquentes
- **Validation automatique** : Pydantic models
- **Documentation auto-générée** : OpenAPI/Swagger

---

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=banking_api --cov-report=html

# Tests spécifiques
pytest tests/test_services.py -v

# Tests avec marqueurs
pytest -m "not slow"
```

### Couverture actuelle

- **Coverage globale** : 86%
- **Services** : 92%
- **Routes** : 85%
- **Utilitaires** : 78%

### Types de tests

- ✅ Tests unitaires des services
- ✅ Tests d'intégration des endpoints
- ✅ Tests de validation des données
- ✅ Tests de performance (cache)

---

## ⚡ Optimisations

### 1. Pagination des clients
**Implémenté par : Ines Ideche**

- Paramètres `skip` et `limit` pour chargement progressif
- Limite maximale de 1000 clients par requête
- Métadonnées de pagination incluses
- **Gain** : -90% temps de réponse pour grandes listes

```python
GET /api/customers?skip=0&limit=100
```

### 2. Cache LRU
**Système de cache en mémoire**

- Mise en cache des DataFrames complets
- Cache des statistiques pré-calculées
- Invalidation automatique si nécessaire
- **Gain** : -95% temps de réponse pour requêtes répétées

### 3. Optimisations Pandas
- Utilisation de `groupby` optimisé
- Opérations vectorisées
- Évitement des boucles Python
- **Gain** : -70% temps de calcul pour agrégations

---

## 🎨 Qualité du code

### Conformité PEP8

```bash
# Vérifier la conformité
flake8 banking_api

# Formater automatiquement
black banking_api
isort banking_api
```

### Vérification de types

```bash
mypy banking_api --ignore-missing-imports
```

### Standards respectés

- ✅ **PEP8** - Style guide Python
- ✅ **Type hints** - Annotations de types
- ✅ **Docstrings** - Documentation des fonctions
- ✅ **Clean Code** - Principes SOLID

---


## 🔄 CI/CD

### GitHub Actions

Le projet utilise 3 workflows automatisés :

#### 1. Tests (`.github/workflows/tests.yml`)
- Exécution sur Python 3.11 et 3.12
- Tests automatiques à chaque push/PR
- Génération de rapports de couverture
- Cache des dépendances pip

#### 2. Linting (`.github/workflows/lint.yml`)
- Vérification PEP8 avec Flake8
- Formatage avec Black
- Tri des imports avec isort
- Type checking avec mypy

#### 3. Deploy (`.github/workflows/deploy.yml`)
- Déploiement automatique en production
- Validation pré-déploiement
- Rollback automatique si échec

### Badges de statut

Les badges en haut de ce README affichent le statut en temps réel :
- ✅ Tests passent
- ✅ Linting conforme
- ✅ Déploiement réussi

---

## 🤝 Contribution

### Workflow Git

1. **Fork** le projet
2. Créer une **branche** (`git checkout -b feature/ma-feature`)
3. **Commit** les changements (`git commit -m 'Add: nouvelle fonctionnalité'`)
4. **Push** vers la branche (`git push origin feature/ma-feature`)
5. Ouvrir une **Pull Request**

### Conventions de commit

- `Add:` - Nouvelle fonctionnalité
- `Fix:` - Correction de bug
- `Update:` - Mise à jour de code existant
- `Refactor:` - Refactorisation
- `Test:` - Ajout/modification de tests
- `Docs:` - Documentation

### Avant de soumettre

```bash
# Vérifier les tests
pytest

# Vérifier le linting
flake8 banking_api
black --check banking_api

# Vérifier la couverture
pytest --cov=banking_api --cov-report=term-missing
```

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👥 Auteurs

**Ines Ideche**
- Optimisations de performance (pagination, cache)
- Architecture API REST
- Documentation technique

---

## 🙏 Remerciements

- FastAPI pour le framework web moderne
- Pandas pour les capacités d'analyse de données
- La communauté Python pour les excellents outils de développement

---

## 📞 Support

Pour toute question ou problème :
1. Consultez la [documentation API](#-documentation-api)
2. Vérifiez les [issues GitHub](https://github.com/CamilleThauvin/projet_python_2_mba/issues)
3. Ouvrez une nouvelle issue si nécessaire

---

<div align="center">

**⭐ Si ce projet vous a été utile, n'hésitez pas à lui donner une étoile ! ⭐**

Made with ❤️ by Ines Hideche

</div>
- [Black Code Formatter](https://black.readthedocs.io/)

---

**Note** : Ces workflows sont configurés pour tourner sur Ubuntu. Pour Windows ou macOS, modifier `runs-on` dans les fichiers YAML.
