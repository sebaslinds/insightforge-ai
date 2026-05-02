from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.database import Base, engine
# Importer les modèles pour que SQLAlchemy les enregistre avant create_all
import core.models          # noqa: F401
import core.tenant_models   # noqa: F401
from api.v1.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crée les tables manquantes au démarrage (idempotent)."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="InsightForge AI",
    version="1.3.0",
    description="Moteur de personnalisation IA multi-tenant pour SaaS",
    lifespan=lifespan,
)

# CORS : wildcard en dev, domaines explicites en production
if settings.ENVIRONMENT == "production":
    origins = [settings.FRONTEND_URL]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "env": settings.ENVIRONMENT, "version": "1.3.0"}

