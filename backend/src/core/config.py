from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path

# Charger le .env explicitement depuis la racine
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

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

    # Étape 7 — Déploiement & GCP
    FRONTEND_URL: str = "http://localhost:3000"
    ENVIRONMENT:  str = "development"   # development | staging | production
    
    # GCP Config
    GOOGLE_CLOUD_PROJECT:       Optional[str] = None
    GCS_BUCKET:                Optional[str] = "insightforge-assets"
    CLOUD_SQL_CONNECTION_NAME: Optional[str] = None # format: "project:region:instance"

    # Business Logic (No more hardcoded data)
    PLAN_PRICES: dict = {"free": 0, "pro": 49, "enterprise": 499}

    class Config:
        extra = "ignore"

@lru_cache
def get_settings():
    return Settings()
