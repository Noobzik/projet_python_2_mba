# Banking Transactions API
## 1. Présentation du Projet
Ce projet consiste en une API REST complète développée avec FastAPI, conçue pour exposer et manipuler des données de transactions bancaires de production. L'API permet la consultation, la recherche multicritère, l'analyse statistique et la détection de fraudes.
Les données ont été prises sur le site kaggle via le lien suivant: https://www.kaggle.com/datasets/ziya07/transaction-data-for-banking-operations
L'API est organisée en 5 catégories principales ayant chacune un rôle. (cf. tableau ci-dessous)

<table>
    <thead>
        <tr>
            <th>Fonctionnalités</th>
            <th>Rôles</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Transactions</td>
            <td>Lecture, pagination, filtrage, recherche avancée multicritères</td>
        </tr>
        <tr>
            <td>Statistiques</td>
            <td>Calcul des agrégations et distributions</td>
        </tr>
        <tr>
            <td>Fraude</td>
            <td>Calcul de taux de fraude, scoring simplifié</td>
        </tr>
        <tr>
            <td>Clients</td>
            <td>Agrégation par client</td>
        </tr>
        <tr>
            <td>Système</td>
            <td>Diagnostic du service et métadonnées</td>
        </tr>
    </tbody>
</table>


Le projet est structuré comme un paquet Python installable, incluant une suite de tests unitaires et une intégration CI/CD.

## 2. Spécifications Techniques
Version : 1.0
Langage : Python 3.12+
Framework : FastAPI, Pandas, Pytest,Uvicorn,
Gestion des dépendances : Setuptools / Poetry
Qualité du code : Linting (flake8), Typage (mypy)


## 3. Structure du Projet
Notre Arborescence
PROJET_PYTHON_2_MBA/
├── .pytest_cache/
├── .vscode/
├── app/
│   ├── __pycache__/
│   ├── router/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── fraude.py
│   │   ├── stats.py
│   │   ├── system.py
│   │   └── transaction.py
│   ├── services/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── customers.py
│   │   ├── stats.py
│   │   ├── system.py
│   │   └── transaction.py
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── mes_commandes.txt
├── data/
│   └── transaction_data.csv  (CSV ici, non versionné)
├── tests/
│   ├── __pycache__/
│   ├── .pytest_cache/
│   ├── __init__.py
│   ├── test_customer.py
│   ├── test_fraud.py
│   ├── test_json_validation.py
│   ├── test_performance.py
│   ├── test_stats_fraud.py
│   ├── test_stats.py
│   ├── test_system.py
│   └── test_transactions.py
├── venv/
├── .coverage
├── .gitignore
├── projet_python.pdf
├── README_PROF.md
├── README.md
└── requirements.txt

Le projet suit une architecture modulaire pour séparer les responsabilités :
* app/routers/ : Points d'entrée de l'API (20 routes totales).
* app/services/ : Logique métier (calculs stats, détection de fraude, etc.).
* tests/ : Suite de tests couvrant au moins 85% du code.


## 4. Installation et Utilisation
### 1. Clonage et Environnement
Bash
Se placer dans le répertoire où se trouvera le projet via le terminal.
git clone https://github.com/florence93600/projet_python_2_mba.git

python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

### 2. Organisation des endpoints (20 routes totales)
* Transactions : Consultation, filtrage, recherche, suppression 
    -GET /api/transactions: Liste paginée des transactions Paramètres : page , limit , type , isFraud , min_amount , max_amount
    -GET /api/transactions/{id}: Détails d’une transaction par son identifiant
    -POST /api/transactions/search: Recherche multicritère (POST avec corps JSON) 
    -GET /api/transactions/types : Liste des types de transactions disponibles (valeurs uniques de type )
    -GET /api/transactions/recent: Renvoie les N dernières transactions du dataset (paramètre n , défaut=10)
    -DELETE /api/transactions/{id}: Supprime une transaction fictive (utilisée uniquement en mode test)
    -GET /api/transactions/by-customer/{customer_id}: Listes des transactions associées à un client (origine)
    -GET /api/transactions/to-customer/{customer_id}: Liste des transactions reçues par un client (destination)

* Statistiques : Agrégations globales et par critères
    -GET /api/stats/overview: Statistiques globales du dataset
    -GET /api/stats/amount-distribution: Histogramme du montant des transactions (en classes de valeurs)  
    -GET /api/stats/by-type: Montant total et nombre moyen de transactions par type 
    -GET /api/stats/daily: Moyenne et volume des transactions par jour ( step )
* Fraude: Analyse et détection
    -GET /api/fraud/summary : Vue d’ensemble de la fraude:
    -GET /api/fraud/by-type : Répartition du taux de fraude par type de transaction
    -POST /api/fraud/predict: Endpoint de scoring pour prédire si une transaction donnée est frauduleuse 
* Customer:  Exploration des portefeuilles clients 
    -GET /api/customers : Liste paginée des clients 
    -GET /api/customers/{customer_id}: Profil client synthétique (nombre de transactions, solde moyen, fraude impliquée, etc.) 
    -GET /api/customers/top : Top clients classés par volume total de transactions Paramètre : n (défaut=10)
* Système: Métadonnées & supervision du service 
    -GET /api/system/health: Vérifie l’état de santé de l’API (ping, latence, chargement du dataset) 
    -GET /api/system/metadata: Informations sur la version du service et la date de dernière mise à jour 

### 3. Lancement de l'API
Bash
uvicorn app.main:app --reload
L'API sera disponible sur http://127.0.0.1:8000. La documentation interactive (Swagger) est accessible via /docs.
### 4. Tests et Qualité
Bash
* Lancer les tests unitaires
pytest --cov=app tests/
#Couverture atteinte:93 %
pytest --cov=app --cov-report=term-missing
### 5. Flux de Travail (Git Flow)
Le développement a été réalisé de manière collaborative par une équipe de 4 personnes 
* Branches de fonctionnalités : Chaque développeur a travaillé sur une branche dédiée.
Florence
Marie-Paule
Carole
Sylvain
* Branche developer : Branche d'intégration où tous les commits sont fusionnés et testés.
* Branche main : Branche de production, mise à jour par Pull Request depuis la branche developer.
### 6.Livraison
Format : Package Python avec tests unitaires via Pull Request GitHub.

