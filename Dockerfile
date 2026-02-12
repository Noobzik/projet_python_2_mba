FROM python:3.11-slim

# Méta-données
LABEL maintainer="Equipe MBA Tech <legodway@gmail.com>"
LABEL description="Banking Transactions API"

# 2. Optimisations Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Dossier de travail
WORKDIR /app

# 4. Outils système (Git est parfois requis par certaines libs, GCC pour compiler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# 5. Installation des dépendances (Cache optimisé)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copie du code source
COPY . .

# 7. Port (Juste pour info, ne fait rien techniquement)
EXPOSE 8000

# 8. Lancement
# OBLIGATOIRE : 0.0.0.0 pour être accessible depuis ton navigateur Windows
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]