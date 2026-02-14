# Banking Transactions API
**MBA 2 - Python - Projet: Exposition de données sous la forme d'une API**

Ce projet consiste à déployer une application complète permettant d'exposer les données de transactions bancaires massives via une API REST robuste. Elle est conçue pour des environnements de production en utilisant le framework FastAPI et une architecture de données Cloud-Native.

---

## 1. Installation et Configuration (Guide Tech Lead)

**Processus Manuel :**
1. **Créer l'environnement virtuel** : `python -m venv venv`
2. **Activer l'environnement** :
   - Windows : `.\venv\Scripts\Activate`
   - Mac/Linux : `source venv/bin/activate`
3. **Installer les dépendances** : `pip install -r requirements.txt`
4. **Configuration du PYTHONPATH** : Indispensable pour que le module `banking_api` soit reconnu par le système.

> **Note importante sur le premier lancement :** Le script téléchargera automatiquement les données nécessaires via la bibliothèque `kagglehub`. Veuillez patienter jusqu'à l'affichage du message : "Système prêt et données chargées."

---

## 2. État d'avancement du projet 

Le socle technique a été finalisé pour assurer une conformité totale aux exigences académiques :

* **Architecture Smart Loader** : Téléchargement automatique et nettoyage des données (Transactions, Fraude, Clients) dès l'initialisation de l'application.
* **Performance** : Traitement intégral en mémoire via Pandas permettant une latence minimale malgré des volumes de données massifs.
* **Qualité du code** : 
  - **Typage** : 100% des variables et signatures de fonctions sont typées.
  - **Normes PEP8** : Conformité validée par l'outil de peluchage `flake8`.
  - **Documentation** : Docstrings descriptives intégrées sur l'ensemble des services métier.
* **Tests et Validation** : 
  - Couverture de code actuelle : **~86%**.
  - Framework `pytest` configuré avec un système de **Mocking** intégral pour isoler les données de test.
* **Routes Système** : Les 22 points d'accès demandés (Transactions, Statistiques, Fraude, Clients, Système) sont pleinement opérationnels.

---

## 3. Organisation des Services

Le projet respecte le principe de séparation des responsabilités (SOC) :



### Transactions
* **Missions** : Liste paginée, recherche multicritère, filtrage par type et par identifiant client.
* **Note Technique** : Implémentation de la suppression logique (exclusion des données en mémoire sans altération de la source).

### Statistiques
* **Missions** : Calcul des indicateurs globaux, distribution des montants et agrégations temporelles sur un cycle de 30 jours.
* **Note Technique** : Optimisation des calculs d'agrégations au sein du module `stats_service.py`.

### Fraude et Scoring
* **Missions** : Synthèse de l'activité frauduleuse et point d'accès de prédiction/scoring en temps réel.
* **Note Technique** : Moteur de règles analytiques basé sur les patterns de virements et les seuils de montants critiques.

### Clients
* **Missions** : Liste exhaustive des clients, profils synthétiques (soldes, volumes d'échanges) et classement des comptes les plus actifs.
* **Note Technique** : Consolidation des données par client via `customers_service.py`.

---

## 4. Standards de Qualité

1. **Typage Strict** : Utilisation systématique des fonctionnalités de typage de Python 3.10+.
2. **Tests Unitaires** : Simulation des données (Mocking) pour garantir des tests rapides et indépendants du dataset source.
3. **Architecture Logicielle** : Séparation stricte entre les modèles de données Pydantic, la logique métier (Services) et les points d'entrée de l'API (Routes).

---

## 5. Commandes Utiles

| Action | Commande |
| :--- | :--- |
| **Lancer l'API (Windows)** | `$env:PYTHONPATH = "src"; uvicorn banking_api.main:app --reload` |
| **Lancer les Tests** | `pytest` |
| **Vérifier la Couverture** | `pytest --cov=src` |
| **Vérifier le Typage** | `mypy src/banking_api` |
| **Vérifier le Style** | `flake8 src/banking_api` |

---
