#!/bin/bash

# Configuration - MODIFIEZ CES VALEURS
PROJECT_ID="insightforge-ai" # Remplacez par votre ID de projet
REGION="northamerica-northeast1"
REPO_NAME="insightforge-repo"

echo "--- Déploiement de InsightForge AI sur Google Cloud Run ---"

# 1. Créer le dépôt Artifact Registry (si pas déjà fait)
echo "[1/4] Vérification du dépôt Artifact Registry..."
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="InsightForge Docker Repository" || echo "Dépôt déjà existant."

# 2. Build et Push du Backend
echo "[2/4] Construction et envoi de l'image BACKEND..."
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/backend ./backend

# 3. Récupérer l'URL du Backend pour le Frontend
# Note: On a besoin de l'URL au moment du build Next.js
echo "[3/4] Construction et envoi de l'image FRONTEND..."
BACKEND_URL="https://backend-458613429367.northamerica-northeast1.run.app"
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/frontend \
    --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL ./frontend

# 4. Déploiement sur Cloud Run
echo "[4/4] Déploiement sur Cloud Run..."

# Déploiement Backend
gcloud run deploy backend \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/backend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --add-cloudsql-instances "${PROJECT_ID}:${REGION}:insightforge-db" \
    --set-env-vars "ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GCS_BUCKET=insightforge-assets-${PROJECT_ID},CLOUD_SQL_CONNECTION_NAME=${PROJECT_ID}:${REGION}:insightforge-db"

# Déploiement Frontend
gcloud run deploy frontend \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/frontend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "NODE_ENV=production,NEXT_PUBLIC_API_URL=$BACKEND_URL"

echo "--- Déploiement terminé ! ---"
echo "URL Backend : $(gcloud run services describe backend --format='value(status.url)' --region $REGION)"
echo "URL Frontend : $(gcloud run services describe frontend --format='value(status.url)' --region $REGION)"
