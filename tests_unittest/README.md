# Tests Unittest - Banking API

Ce dossier contient les tests unitaires utilisant le framework `unittest` standard de Python.

## Structure des tests

- `test_transactions_service.py` : 16 tests pour le service de transactions
- `test_stats_service.py` : 6 tests pour le service de statistiques
- `test_fraud_detection_service.py` : 8 tests pour le service de détection de fraude
- `test_customer_service.py` : 11 tests pour le service clients

## Lancer les tests

### Tous les tests
```bash
python -m unittest discover tests_unittest
```

### Avec verbosité
```bash
python -m unittest discover tests_unittest -v
```

### Un fichier spécifique
```bash
python -m unittest tests_unittest.test_transactions_service
```

### Une classe spécifique
```bash
python -m unittest tests_unittest.test_transactions_service.TestTransactionsService
```

### Un test spécifique
```bash
python -m unittest tests_unittest.test_transactions_service.TestTransactionsService.test_get_paginated_transactions
```

## Avec couverture de code

```bash
coverage run -m unittest discover tests_unittest
coverage report
coverage html
```

## Différences avec Pytest

Les tests unittest utilisent:
- `unittest.TestCase` au lieu de fonctions simples
- `setUp()` / `tearDown()` au lieu de fixtures pytest
- `self.assertEqual()` au lieu de `assert`
- `patch` de `unittest.mock` pour le mocking

## Notes

Les tests unittest et pytest testent les mêmes fonctionnalités mais avec des syntaxes différentes, conformément aux exigences du projet.
