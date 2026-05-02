from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "InsightForge AI"
    DATABASE_URL: str = "postgresql://postgres:secret@localhost:5432/insightforge"
    OPENAI_API_KEY: str = ""

    # Étape 6 — Alertes
    SLACK_WEBHOOK_URL:    Optional[str] = None
    RESEND_API_KEY:       Optional[str] = None
    ALERT_EMAIL_FROM:     str = "alerts@insightforge.ai"
    ALERT_EMAIL_TO:       str = "admin@insightforge.ai"
    CHURN_ALERT_THRESHOLD: float = 0.7

    # Étape 7 — Déploiement
    FRONTEND_URL: str = "http://localhost:3000"
    ENVIRONMENT:  str = "development"   # development | staging | production

    class Config:
        env_file = "../../.env"
        extra = "ignore"

@lru_cache
def get_settings():
    return Settings()
