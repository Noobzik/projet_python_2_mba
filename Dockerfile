# Dockerfile pour l’API Banking Transactions
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Définir les variables d’environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements en premier pour optimiser le cache Docker
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code de l’application
COPY banking_api/ ./banking_api/
COPY data/ ./data/

# Exposer le port
EXPOSE 8000

# Vérification de santé du conteneur
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/api/system/health')" || exit 1

# Lancer l’application
CMD ["uvicorn", "banking_api.main:app", "--host", "0.0.0.0", "--port", "8000"]