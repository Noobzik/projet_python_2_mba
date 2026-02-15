# Guide d'installation - Banking Transactions API

## Installation depuis PyPI (futur)

```bash
pip install banking-transactions-api
```

## Installation depuis le code source

### 1. Cloner le repository

```bash
git clone https://github.com/CamilleThauvin/projet_python_2_mba.git
cd projet_python_2_mba
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installer les dépendances de développement (optionnel)

```bash
pip install -r requirements-dev.txt
```

### 5. Télécharger les données

Placez le fichier `transactions_data.csv` dans le dossier `data/`.

## Installation du package en mode développement

```bash
pip install -e .
```

Cela installe le package en mode "editable", permettant de modifier le code sans réinstaller.

## Installation avec les extras

### Installation avec outils de développement

```bash
pip install -e ".[dev]"
```

### Installation avec outils de test

```bash
pip install -e ".[test]"
```

## Vérifier l'installation

```bash
# Vérifier que le package est installé
pip show banking-transactions-api

# Lancer les tests
pytest tests/
python -m unittest discover tests_unittest

# Vérifier PEP8
make lint
```

## Lancer l'API

```bash
uvicorn banking_api.main:app --reload
```

L'API sera accessible sur http://localhost:8000

Documentation interactive: http://localhost:8000/docs

## Désinstallation

```bash
pip uninstall banking-transactions-api
```

## Build du package

### Créer une distribution wheel

```bash
python -m build --wheel
```

Le fichier `.whl` sera créé dans le dossier `dist/`.

### Installer le wheel localement

```bash
pip install dist/banking_transactions_api-1.0.0-py3-none-any.whl
```

## Dépannage

### Erreur "Module not found"

Assurez-vous que l'environnement virtuel est activé:
```bash
source venv/bin/activate
```

### Erreur "Fichier de données non trouvé"

Vérifiez que `data/transactions_data.csv` existe.

### Tests qui échouent

Assurez-vous d'avoir installé les dépendances de test:
```bash
pip install -r requirements-test.txt
```
