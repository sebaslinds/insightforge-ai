# Guide de Déploiement GCP - InsightForge AI

Ce guide vous accompagne dans le déploiement complet de la solution InsightForge AI sur Google Cloud Platform.

## 1. Prérequis
- Un compte **Google Cloud** avec une facturation active.
- **Google Cloud SDK (gcloud CLI)** installé sur votre machine.
- Le code source du projet en local.

## 2. Préparation du projet GCP
1. Créez un nouveau projet sur la [Console GCP](https://console.cloud.google.com/).
2. Notez votre **PROJECT_ID** (ex: `insightforge-ai-12345`).
3. Authentifiez-vous en local :
   ```powershell
   gcloud auth login
   gcloud auth application-default login
   ```

## 3. Configuration de l'Infrastructure (Automatisée)
Utilisez le script de configuration pour activer les APIs et créer les comptes de service nécessaires.

**Sur Windows (PowerShell) :**
Modifiez `$PROJECT_ID` dans `setup_gcp.sh` (ou adaptez les commandes) puis lancez :
```powershell
# Note: Le script .sh nécessite un environnement Bash (Git Bash, WSL)
./setup_gcp.sh
```

**Ce que fait ce script :**
- Active les APIs : Compute, Cloud SQL, Storage, Cloud Run, Cloud Build.
- Crée un bucket **Cloud Storage** pour les assets ML.
- Crée un **Compte de Service** avec les droits nécessaires.
- Génère un fichier `gcp-key.json` (à conserver précieusement).

## 4. Base de Données (Cloud SQL)
Le déploiement attend une instance PostgreSQL nommée `insightforge-db`.
1. Allez dans **SQL** -> **Créer une instance**.
2. Choisissez **PostgreSQL**.
3. ID de l'instance : `insightforge-db`.
4. Mot de passe : Notez-le bien (il sera utilisé dans les variables d'env).
5. Région : `northamerica-northeast1` (ou celle de votre choix).

## 5. Déploiement (Cloud Run)
Utilisez le script de déploiement qui gère le build Docker et l'envoi sur Cloud Run.

**Sur Windows :**
1. Ouvrez `deploy_gcp.ps1`.
2. Mettez à jour `$PROJECT_ID` (ligne 2).
3. Mettez à jour les variables d'environnement (ligne 43) :
   - `DB_PASS` : Votre mot de passe Cloud SQL.
   - `REGION` : Votre région.
4. Exécutez le script :
   ```powershell
   ./deploy_gcp.ps1
   ```

**Sur Linux/Mac :**
Utilisez `./deploy_gcp.sh` avec une logique similaire.

## 6. Post-Déploiement
Une fois le script terminé, vous obtiendrez deux URLs :
- **Backend URL** : À configurer dans le frontend si nécessaire.
- **Frontend URL** : Votre point d'accès utilisateur.

### Variables d'environnement critiques (Production)
Assurez-vous que ces variables sont bien définies dans la console Cloud Run pour le **backend** :
- `DATABASE_URL` : Format `postgresql://user:pass@/dbname?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_ID`
- `OPENAI_API_KEY` : Votre clé OpenAI pour les recommandations.
- `ENVIRONMENT` : `production`

---
> [!TIP]
> Pour plus de sécurité, utilisez **Secret Manager** pour stocker `DATABASE_URL` et `OPENAI_API_KEY` au lieu de les mettre en clair dans les scripts.
