# Dockerfile pour Banking Transactions API

FROM python:3.12-slim

# Métadonnées
LABEL maintainer="ESG MBA Team <team@esg-mba.com>"
LABEL version="1.0.0"
LABEL description="Banking Transactions API - FastAPI Application"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer un utilisateur non-root
RUN useradd -m -u 1000 apiuser

# Répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY banking_api/ ./banking_api/
COPY data/ ./data/

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs && \
    chown -R apiuser:apiuser /app

# Utiliser l'utilisateur non-root
USER apiuser

# Exposer le port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/system/health')" || exit 1

# Commande de démarrage
CMD ["uvicorn", "banking_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
