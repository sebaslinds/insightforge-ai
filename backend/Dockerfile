FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système (nécessaires pour psycopg2 et Cloud SQL connector)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src /app/src

# Ajouter le src au PYTHONPATH
ENV PYTHONPATH=/app/src

EXPOSE 8000

# Cloud Run utilise la variable d'environnement PORT
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
