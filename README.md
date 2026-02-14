<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
</head>
<body>

<h1>Banking Transactions API</h1>

<h2>1. Présentation du Projet</h2>

<p>
Ce projet consiste en une API REST complète développée avec FastAPI, conçue pour exposer et manipuler des données de transactions bancaires de production. 
L'API permet la consultation, la recherche multicritère, l'analyse statistique et la détection de fraudes.
</p>

<p>
Les données ont été prises sur le site kaggle via le lien suivant :
https://www.kaggle.com/datasets/ziya07/transaction-data-for-banking-operations
</p>

<p>
L'API est organisée en 5 catégories principales ayant chacune un rôle.
</p>

<table border="1">
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

<p>
Le projet est structuré comme un paquet Python installable, incluant une suite de tests unitaires et une intégration CI/CD.
</p>

<h2>2. Spécifications Techniques</h2>

<ul>
    <li>Version : 1.0</li>
    <li>Langage : Python 3.12+</li>
    <li>Framework : FastAPI, Pandas, Pytest, Uvicorn</li>
    <li>Gestion des dépendances : Setuptools / Poetry</li>
    <li>Qualité du code : Linting (flake8), Typage (mypy)</li>
</ul>

<h2>3. Structure du Projet</h2>

<p>Notre Arborescence</p>

<pre>
PROJET_PYTHON_2_MBA/
├── app/
│   ├── router/
│   ├── services/
│   ├── config.py
│   ├── main.py
├── data/
│   └── transaction_data.csv
├── tests/
├── README.md
└── requirements.txt
</pre>

<p>
Le projet suit une architecture modulaire pour séparer les responsabilités :
</p>

<ul>
    <li>app/routers/ : Points d'entrée de l'API (20 routes totales).</li>
    <li>app/services/ : Logique métier.</li>
    <li>tests/ : Suite de tests couvrant au moins 85% du code.</li>
</ul>

<h2>4. Installation et Utilisation</h2>

<h3>1. Clonage et Environnement</h3>

<pre>
git clone https://github.com/florence93600/projet_python_2_mba.git

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
</pre>

<h3>2. Organisation des endpoints</h3>

<h4>Transactions</h4>
<ul>
    <li>GET /api/transactions</li>
    <li>GET /api/transactions/{id}</li>
    <li>POST /api/transactions/search</li>
    <li>GET /api/transactions/types</li>
    <li>GET /api/transactions/recent</li>
    <li>DELETE /api/transactions/{id}</li>
    <li>GET /api/transactions/by-customer/{customer_id}</li>
    <li>GET /api/transactions/to-customer/{customer_id}</li>
</ul>

<h4>Statistiques</h4>
<ul>
    <li>GET /api/stats/overview</li>
    <li>GET /api/stats/amount-distribution</li>
    <li>GET /api/stats/by-type</li>
    <li>GET /api/stats/daily</li>
</ul>

<h4>Fraude</h4>
<ul>
    <li>GET /api/fraud/summary</li>
    <li>GET /api/fraud/by-type</li>
    <li>POST /api/fraud/predict</li>
</ul>

<h4>Customer</h4>
<ul>
    <li>GET /api/customers</li>
    <li>GET /api/customers/{customer_id}</li>
    <li>GET /api/customers/top</li>
</ul>

<h4>Système</h4>
<ul>
    <li>GET /api/system/health</li>
    <li>GET /api/system/metadata</li>
</ul>

<h3>3. Lancement de l'API</h3>

<pre>
uvicorn app.main:app --reload
</pre>

<p>
L'API sera disponible sur http://127.0.0.1:8000. La documentation interactive est accessible via /docs.
</p>

<h3>4. Tests et Qualité</h3>

<pre>
pytest --cov=app tests/
pytest --cov=app --cov-report=term-missing
</pre>

<p>Couverture atteinte : 93%</p>

<h2>5. Flux de Travail (Git Flow)</h2>

<p>
Le développement a été réalisé de manière collaborative par une équipe de 4 personnes.
</p>

<ul>
    <li>Branches de fonctionnalités : Florence, Marie-Paule, Carole, Sylvain</li>
    <li>Branche developer : Branche d'intégration</li>
    <li>Branche main : Branche de production</li>
</ul>

<h2>6. Livraison</h2>

<p>
Format : Package Python avec tests unitaires via Pull Request GitHub.
</p>

</body>
</html>
