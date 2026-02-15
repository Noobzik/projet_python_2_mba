FROM python:3.11-slim

WORKDIR /app
# Copier le code de l'application
COPY banking_api/ ./banking_api/
# Copier les fichiers de requirements
COPY pyproject.toml ./

# Installer les dépendances
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Exposer le port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

# Commande de démarrage
CMD ["uvicorn", "banking_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
