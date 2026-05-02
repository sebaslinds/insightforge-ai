#!/bin/bash

# Configuration - MODIFIEZ CES VALEURS
PROJECT_ID="insightforge-prod"
REGION="us-central1"
BUCKET_NAME="insightforge-assets-${PROJECT_ID}"
SERVICE_ACCOUNT_NAME="insightforge-sa"

echo "--- Début de la configuration GCP pour InsightForge AI ---"

# 1. Configurer le projet actif
gcloud config set project $PROJECT_ID

# 2. Activer les APIs nécessaires
echo "[1/4] Activation des APIs GCP..."
gcloud services enable compute.googleapis.com \
                       sqladmin.googleapis.com \
                       storage.googleapis.com \
                       run.googleapis.com \
                       cloudbuild.googleapis.com

# 3. Créer le Bucket Cloud Storage
echo "[2/4] Création du bucket GCS : $BUCKET_NAME..."
gsutil mb -l $REGION gs://$BUCKET_NAME/

# 4. Créer le Compte de Service et attribuer les rôles
echo "[3/4] Configuration du compte de service : $SERVICE_ACCOUNT_NAME..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --description="Service account for InsightForge AI Application" \
    --display-name="InsightForge SA"

# Attribuer les rôles IAM
ROLES=("roles/cloudsql.client" "roles/storage.objectAdmin" "roles/run.developer")

for ROLE in "${ROLES[@]}"; do
    echo "  -> Attribution du rôle $ROLE..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$ROLE"
done

# 5. Créer une clé JSON pour le développement local (optionnel)
echo "[4/4] Génération de la clé JSON pour le développement local..."
gcloud iam service-accounts keys create ./gcp-key.json \
    --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

echo "--- Configuration terminée ---"
echo "Fichiers créés :"
echo " - ./gcp-key.json (À AJOUTER DANS .gitignore ET UTILISER POUR GOOGLE_APPLICATION_CREDENTIALS)"
echo "Bucket créé : gs://$BUCKET_NAME"
echo "---"
