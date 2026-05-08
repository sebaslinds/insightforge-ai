param (
    [string]$service = "all" # Valeurs: all, backend, frontend
)

# Configuration
$PROJECT_ID = "insightforge-ai-495422"
$REGION = "northamerica-northeast1"
$REPO_NAME = "insightforge-repo"

Write-Host "--- Déploiement de InsightForge AI ($service) sur Google Cloud Run ---" -ForegroundColor Cyan

$GCLOUD_PATH = "$env:LocalAppData\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
if (-not (Test-Path $GCLOUD_PATH)) { $GCLOUD_PATH = "gcloud" }

# 1. Configurer le projet
Write-Host "[1/5] Configuration du projet $PROJECT_ID..."
& $GCLOUD_PATH config set project $PROJECT_ID

# 2. Vérification du dépôt
Write-Host "[2/5] Vérification du dépôt Artifact Registry..."
& $GCLOUD_PATH artifacts repositories create $REPO_NAME --repository-format=docker --location=$REGION --description="InsightForge Docker Repository" 2>$null

# 3. Build et Push du Backend (Uniquement si all ou backend)
if ($service -eq "all" -or $service -eq "backend") {
    Write-Host "[3/5] Construction et envoi de l'image BACKEND..." -ForegroundColor Yellow
    & $GCLOUD_PATH builds submit --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/backend" ./backend
}

# 4. Build et Push du Frontend (Uniquement si all ou frontend)
if ($service -eq "all" -or $service -eq "frontend") {
    Write-Host "Récupération de l'URL du backend..."
    $backendUrl = & $GCLOUD_PATH run services describe backend --format='value(status.url)' --region $REGION 2>$null
    if (-not $backendUrl) { $backendUrl = "https://backend-gqaawjux7q-nn.a.run.app" }

    Write-Host "[4/5] Construction et envoi de l'image FRONTEND..." -ForegroundColor Yellow
    & $GCLOUD_PATH builds submit --config ./frontend/cloudbuild.yaml `
        --substitutions="_NEXT_PUBLIC_API_URL=$backendUrl,_TAG=${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/frontend" ./frontend
}

# 5. Déploiement sur Cloud Run
Write-Host "[5/5] Déploiement sur Cloud Run..." -ForegroundColor Yellow

if ($service -eq "all" -or $service -eq "backend") {
    & $GCLOUD_PATH run deploy backend `
        --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/backend" `
        --platform managed --region $REGION --allow-unauthenticated `
        --add-cloudsql-instances "${PROJECT_ID}:${REGION}:insightforge-db" `
        --service-account "insightforge-app-sa@${PROJECT_ID}.iam.gserviceaccount.com" `
        --set-env-vars "ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GCS_BUCKET=insightforge-assets-${PROJECT_ID},CLOUD_SQL_CONNECTION_NAME=${PROJECT_ID}:${REGION}:insightforge-db,DB_USER=postgres,DB_PASS=ForgeAI2026,DB_NAME=insightforge,OPENAI_API_KEY=PLACEHOLDER_KEY"
}

if ($service -eq "all" -or $service -eq "frontend") {
    & $GCLOUD_PATH run deploy frontend `
        --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/frontend" `
        --platform managed --region $REGION --allow-unauthenticated `
        --set-env-vars "NODE_ENV=production"
}

Write-Host "--- Déploiement terminé ! ---" -ForegroundColor Green
