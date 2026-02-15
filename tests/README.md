# Tests Pytest - Banking API

Ce dossier contient les tests unitaires pour l'API Banking Transactions.

## Structure des tests

- `conftest.py` : Fixtures partagées (client API, mock CSV)
- `test_transactions_service.py` : Tests pour le service de transactions
- `test_stats_service.py` : Tests pour le service de statistiques
- `test_fraud_detection_service.py` : Tests pour le service de détection de fraude
- `test_customer_service.py` : Tests pour le service clients
- `test_error_handling.py` : Tests de gestion d'erreurs
- `test_edge_cases.py` : Tests des cas limites
- `test_convert_types.py` : Tests des fonctions utilitaires

## Lancer les tests

### Tous les tests
```bash
pytest tests/
```

### Avec couverture de code
```bash
pytest tests/ --cov=banking_api/services --cov-report=term
```

### Avec rapport HTML
```bash
pytest tests/ --cov=banking_api/services --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

### Tests verbeux
```bash
pytest tests/ -v
```

### Un fichier spécifique
```bash
pytest tests/test_transactions_service.py
```

### Un test spécifique
```bash
pytest tests/test_transactions_service.py::test_get_paginated_transactions
```

## Couverture actuelle

**84%** de couverture sur les services (79 tests)

### Détail par module
- `transactions_service.py` : 83%
- `stats_service.py` : 84%
- `fraud_detection_service.py` : 88%
- `customer_service.py` : 83%

## Fixtures disponibles

- `client` : Client TestClient FastAPI pour tester les routes
- `sample_csv_path` : Fichier CSV temporaire avec données de test
- `mock_csv_path` : Mock du chemin CSV pour les services

## Notes

Les tests utilisent des données fictives créées à la volée pour éviter de dépendre du gros fichier CSV de production.
