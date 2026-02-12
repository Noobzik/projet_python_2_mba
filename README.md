#  Banking Transactions API
**MBA 2 - Python - Projet: Exposition de données sous la forme d'une API**

| **Équipe** | **Banking Transactions API** |
| :--- | :--- |
| **Tech Lead** | **Godwin Ayita** |
| **Membres** | **Lilian NGOUNGOU (Dev A)**, **Clément CORNUAULT (Dev B)**, **Ruth NGO MBEM (Dev C)**, **Johann THEBAULT (Dev D** |
| **Promotion** | MBA 2 - Big Data & AI |



Ce projet consiste à déployer une application complète permettant d'exposer les données de transactions bancaires massives via une API REST robuste. Elle est conçue pour des environnements de production en utilisant le framework **FastAPI** et une architecture de données "Cloud-Native".

---

##  1. Installation & Configuration (Guide Tech Lead)

**Processus Docker (Recommandé) :** Pour une isolation totale et une gestion simplifiée du dataset.

1. **Cloner le projet** depuis GitHub.
2. **Lancer avec Docker-Compose** : `docker-compose up --build`.
   - *Le dataset est géré via un volume pour éviter les re-téléchargements.*

**Processus Manuel :**
1. **Créer l'environnement virtuel** : `python -m venv venv`.
2. **Activer l'environnement** :
   - Windows : `.\venv\Scripts\Activate`
   - Mac/Linux : `source venv/bin/activate`
3. **Installer les dépendances** : `pip install -r requirements.txt`.
4. **Installer le paquet en mode "editable"** : `pip install -e .`.
   - *Note : Cela permet à Python de reconnaître le dossier `app` comme un module installable via setuptools.*

>  **Premier Lancement :** Le script téléchargera automatiquement les données via `kagglehub`. **Attendez le message "✅ API prête à recevoir des requêtes."**.

---

##  2. État d'avancement du projet


* **Architecture "Smart Merge"** : Fusion automatique en mémoire des Transactions, de la Fraude (`isFraud`) et des données Clients/Cartes au démarrage.
* **Performance** : Chargement optimisé pour une latence < 500ms pour 100 transactions filtrées.
* **Qualité du code** : 
  - **Typage** : 100% des variables typées (Validation `mypy` OK).
  - **PEP8** : Conformité totale via `flake8`.
  - **Documentation** : Style NumPy appliqué systématiquement.
* **Tests** : 
  - Couverture actuelle : **> 95%**.
  - Frameworks `pytest` (unitaires) et `unittest` (features) configurés.
* **Routes Système** : Les 22 routes (Transactions, Stats, Fraude, Clients, Admin) sont opérationnelles.

---

##  3. Organisation des Services

Le projet respecte la séparation des responsabilités demandée :

###  Transactions (Routes 1 à 8) 
* **Missions** : Liste paginée, recherche multi-critère, filtrage par type et par client.

###  Statistiques (Routes 9 à 12) 
* **Missions** : Statistiques globales, distribution des montants (histogrammes), agrégations journalières.

###  Fraude & Scoring (Routes 13 à 15) 
* **Missions** : Vue d'ensemble de la fraude et endpoint de prédiction/scoring.

###  Clients (Routes 16 à 18) - *Dev D*
* **Missions** : Liste des clients, profil synthétique et Top clients.

---

##  4. Standards de Qualité (Strictement obligatoires)

Pour garantir la conformité au barème final :

1. **Typage Strict** : 100% des variables et retours de fonctions sont typés.
2. **Tests Unitaires** : Minimum 1 test par endpoint avec couverture cible > 85%.
3. **Docstrings NumPy** : Obligatoire pour la documentation complète du code source.
4. **Git Workflow** : Livraison effectuée sous forme de **Pull Request (PR)** sur la branche principale.

---

##  5. Commandes Utiles

| Action | Commande |
| :--- | :--- |
| **Lancer l'API** | `uvicorn app.main:app --reload` |
| **Lancer les Tests** | `python -m pytest --cov=app` |
| **Vérifier le Typage** | `mypy app` |
| **Vérifier le Style** | `flake8 app` |
| **Lancer via Docker** | `docker-compose up --build` |

