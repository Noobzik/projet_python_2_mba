# 📘 Banking Transactions API — FastAPI Project

## 🎓 ESG MBA – Évaluation de fin de cours  
**MBA 2 – Python – Exposition de données sous forme d’API**

---

## 📌 Présentation du projet

Ce projet consiste à développer une **API REST complète avec FastAPI** permettant d’exposer, filtrer et analyser des données de transactions bancaires fictives.

L’API est conçue pour une application métier de **gestion de portefeuilles clients bancaires** et répond aux exigences académiques suivantes :

- ✅ Qualité et structuration du code
- ✅ Respect des standards Python (PEP8, typage)
- ✅ Tests unitaires et fonctionnels
- ✅ Packaging avec `pyproject.toml`
- ✅ Conteneurisation avec Docker
- ✅ Intégration Continue (CI/CD) via GitHub Actions
- ✅ Déploiement cloud en production

---

## 🌍 Déploiement en production

L’API est déployée en environnement cloud.

🔗 **Documentation interactive (Swagger UI)** :  
👉 https://projet-python-2-mba.onrender.com/docs  

🔗 **URL racine de l’API** :  
👉 https://projet-python-2-mba.onrender.com  

🔗 **Dashboard de consommation de notre api** :  
👉 https://fraudbank.onrender.com/  

Le déploiement est automatisé via pipeline CI/CD et synchronisé avec la branche principale du dépôt.

---

## ⚙️ Stack technique

- **FastAPI** — Framework API moderne et performant  
- **Pydantic** — Validation et sérialisation des données  
- **Pytest** — Tests unitaires et fonctionnels  
- **Docker** — Conteneurisation  
- **GitHub Actions** — Intégration Continue  
- **Render** — Hébergement cloud  

---

## 👥 Équipe projet

| Nom                 | Email |
|---------------------|-------|
| **Idriss MBE**      | i_mbe@stu-mba-esg.com |
| **Nadiath SAKA**    | n_saka@stu-mba-esg.com |
| **Michele FAMENI**  | m_fameni@stu-mba-esg.com |
| **Raouf OROUGOURA** | r_orougoura@stu-mba-esg.com |

---

## 🧱 Architecture du projet

```text
FastApi/
│
├── .github/
│   └── workflows/         # CI GitHub Actions
│
├── app/                   # Application FastAPI
│   ├── __init__.py
│   ├── main.py            # Point d'entrée
│   ├── routers/           # Endpoints API
│   ├── services/          # Logique métier
│   ├── models/            # Schémas Pydantic
│   ├── utils/             # Fonctions utilitaires
│   └── data/              # Gestion du dataset
│       ├── import_data.py
│       ├── load_data.py
│       └── datasets/
│
├── test/
│   ├── unit/
│   └── feature/
│
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
