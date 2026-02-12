# Guide de démarrage rapide

## Installation rapide

```powershell
# 1. Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Installer les dépendances de développement (optionnel)
pip install -r requirements-dev.txt

# 4. Vérifier l'installation
python -c "import banking_api; print('Installation réussie!')"
```

## Lancer l'application

```powershell
# Démarrer le serveur
uvicorn banking_api.main:app --reload

# L'API sera disponible sur http://localhost:8000
# Documentation interactive: http://localhost:8000/docs
```

## Exécuter les tests

```powershell
# Tests pytest
pytest --cov=banking_api

# Tests unittest
python -m unittest discover tests/features
```

## Vérifier la qualité du code

```powershell
# Linting
flake8 banking_api/

# Type checking
mypy banking_api/

# Formatage
black banking_api/ tests/
```

## Construire le package

```powershell
# Utiliser le script PowerShell (recommandé)
.\build.ps1

# Ou manuellement:
# Installer build
pip install build

# Construire
python -m build

# Les fichiers seront dans dist/
```

## Commandes utiles

```powershell
# Installer le package en mode développement
pip install -e .

# Générer un rapport de couverture HTML
pytest --cov=banking_api --cov-report=html
start htmlcov/index.html

# Lister toutes les routes disponibles
python -c "from banking_api.main import app; print([route.path for route in app.routes])"
```

## Résolution des problèmes

### Les imports ne fonctionnent pas

```powershell
# Assurez-vous que l'environnement virtuel est activé
.\venv\Scripts\Activate.ps1

# Réinstallez les dépendances
pip install -r requirements.txt
```

### Les données ne se chargent pas

```powershell
# Vérifiez que les fichiers CSV/JSON sont dans data/
ls data/

# Les fichiers requis:
# - transactions_data.csv
```

### Erreurs de tests

```powershell
# Nettoyez le cache pytest
Remove-Item -Recurse -Force .pytest_cache

# Relancez les tests
pytest -v
```
