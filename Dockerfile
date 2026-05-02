FROM python:3.11-slim

# Évite les fichiers .pyc et les buffers stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python en premier (cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY backend/src ./src
COPY backend/src/services/ml/models ./src/services/ml/models

WORKDIR /app/src

EXPOSE 8000

# Render injecte $PORT, fallback 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
