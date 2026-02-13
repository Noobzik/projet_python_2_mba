# Utilisation d'une image Python légère
FROM python:3.11-slim

# Définition du dossier de travail dans le container
WORKDIR /app

# Copie des fichiers de dépendances
COPY pyproject.toml .

# Installation des dépendances
RUN pip install .

# Copie du reste du code et du dataset
COPY src/ ./src/
COPY transactions_data.csv .

# Exposition du port utilisé par FastAPI
EXPOSE 8000

# Commande de lancement de l'API
CMD ["uvicorn", "src.banking_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
