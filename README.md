# Banking Transactions API

API REST développée avec FastAPI expose et analyse des données de transactions bancaires fictives.

## Installation

```bash
pip install -e ".[dev]"
```

## Lancement

```bash
# Placer le CSV dans data/transactions_data.csv
banking-api
# ou
uvicorn banking_api.main:app --reload
```

L'API est disponible sur http://localhost:8000 — Swagger UI sur http://localhost:8000/docs

## Tests

```bash
pytest --cov=banking_api
python -m unittest discover tests/features
```

## Packaging

```bash
python -m build
```
