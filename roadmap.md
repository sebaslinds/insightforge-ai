# InsightForge AI — Roadmap pas a pas

## Etat actuel (mis a jour 2026-05-01 — v1.3.0)

### Termine
- [x] Backend FastAPI structure (`backend/src/`)
- [x] Frontend Next.js 14 — Tailwind, Recharts, Glassmorphism, i18n EN/FR
- [x] Dashboard : KPIs, graphique + slicer, segments, copilot, ML, Decision Engine
- [x] PostgreSQL — tables `users` + `events` avec 2000 users / 76 000 events
- [x] XGBoost churn model — 75.5% accuracy — `churn_model.pkl` sauvegarde
- [x] K-Means segmentation — silhouette 0.2537 — 4 profils actifs
- [x] Endpoints ML : `/ml/churn-scores`, `/ml/segments`, `/ml/metrics`
- [x] GPT-4o branche dans `ai_service.py` (async, avec fallback mock)
- [x] `/ask` endpoint entierement async (SQL + DB + Decision + GPT-4o)

---

## Etape 5 — Authentification & Multi-tenant [TERMINE ✅]

> **Résultat :** Tables `tenants` + `api_keys` créées automatiquement au démarrage.
> Header `X-API-Key: if_xxx` requis pour les endpoints protégés.

### Fichiers créés
- `core/security.py`        → middleware `get_current_tenant()`
- `core/tenant_models.py`   → ORM Tenant + ApiKey
- `api/v1/admin.py`         → endpoints CRUD tenants + clés

### Endpoints admin
```
POST   /admin/tenants                          → créer tenant
GET    /admin/tenants                          → lister tenants
POST   /admin/tenants/{slug}/api-keys?label=X  → générer clé (prefix if_)
DELETE /admin/api-keys/{key_id}                → révoquer clé
```

### Test rapide
```bash
# 1. Créer un tenant
curl -X POST http://localhost:8000/admin/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp", "slug": "acme", "plan": "pro"}'

# 2. Générer une API Key
curl -X POST "http://localhost:8000/admin/tenants/acme/api-keys?label=Prod"
# → Retourne : { "key": "if_GbJNu6..." }

# 3. Utiliser la clé
curl http://localhost:8000/ml/metrics -H "X-API-Key: if_GbJNu6..."
```

---

## Etape 6 — Alertes automatiques (Slack / Email) [TERMINE ✅]

> **Résultat :** Alertes Slack webhook réelles + Email Resend.
> Fallback console si les vars d'env sont absentes.

### Fichiers modifiés/créés
- `services/automation/slack_alerts.py`  → Slack webhook + Resend email + `trigger_churn_alert()`
- `api/v1/alerts.py`                     → endpoints `/alerts/churn` + `/alerts/scan-churn`

### Variables d'environnement à ajouter dans `.env`
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
RESEND_API_KEY=re_...
ALERT_EMAIL_FROM=alerts@insightforge.ai
ALERT_EMAIL_TO=admin@insightforge.ai
CHURN_ALERT_THRESHOLD=0.7   # défaut : 0.70
```

### Endpoints alertes
```
POST /alerts/churn        → alerte manuelle pour un user
POST /alerts/scan-churn   → scan tous les users > seuil (background)
```

### Logique automatique
- `churn_score >= 0.85` → priority `high`  🚨
- `churn_score >= 0.70` → priority `medium` ⚠️
- Slack : bloc formaté avec user_id, segment, score, recommandation
- Email : HTML complet via Resend API

---

## Etape 7 — Deploiement [PRET]

| Service  | Plateforme        | Commande                      |
|----------|-------------------|-------------------------------|
| Frontend | Vercel            | `vercel deploy`               |
| Backend  | Render            | `Dockerfile` + `uvicorn main:app` |
| DB       | Render PostgreSQL | Connection string dans `.env` |

### Checklist deploiement
- [x] `requirements.txt` à jour (17 dépendances)
- [x] `Dockerfile` créé et optimisé pour Render (`$PORT` dynamique)
- [x] CORS mis à jour (`ENVIRONMENT=production` → restreint à `FRONTEND_URL`)
- [x] Endpoint `/health` disponible pour les health checks Render/Vercel
- [ ] Variables d'environnement configurées sur Render/Vercel
- [ ] `ENVIRONMENT=production` + `FRONTEND_URL=https://your-app.vercel.app`
- [ ] Test end-to-end en staging avant production

### Commandes déploiement backend (Render)
```bash
# Sur Render : Build Command
pip install -r requirements.txt

# Start Command (Render injecte $PORT)
cd backend/src && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Commandes déploiement frontend (Vercel)
```bash
cd frontend
vercel deploy --prod
# Variables à configurer sur Vercel :
# NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## Variables d'environnement production (Render + Vercel)

```env
# Backend (Render)
DATABASE_URL=postgresql://user:pass@host:5432/insightforge
OPENAI_API_KEY=sk-...
ENVIRONMENT=production
FRONTEND_URL=https://insightforge.vercel.app
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
RESEND_API_KEY=re_...
ALERT_EMAIL_FROM=alerts@insightforge.ai
ALERT_EMAIL_TO=admin@insightforge.ai
CHURN_ALERT_THRESHOLD=0.7

# Frontend (Vercel)
NEXT_PUBLIC_API_URL=https://insightforge-api.onrender.com
```

---

## Etat des 12 endpoints actifs (v1.3.0)

| Endpoint | Méthode | Tag | Description |
|----------|---------|-----|-------------|
| `/health` | GET | System | Health check |
| `/ask/` | POST | Copilot | GPT-4o analyst |
| `/decision/` | POST | Decision | Decision Engine |
| `/ml/metrics` | GET | ML | Accuracy + silhouette |
| `/ml/segments` | GET | ML | 4 profils K-Means |
| `/ml/churn-scores` | GET | ML | Top 50 risque churn |
| `/ml/train` | POST | ML | Ré-entraînement |
| `/admin/tenants` | GET/POST | Admin | CRUD tenants |
| `/admin/tenants/{slug}/api-keys` | POST | Admin | Générer clé |
| `/admin/api-keys/{id}` | DELETE | Admin | Révoquer clé |
| `/alerts/churn` | POST | Alerts | Alerte manuelle |
| `/alerts/scan-churn` | POST | Alerts | Scan auto background |
