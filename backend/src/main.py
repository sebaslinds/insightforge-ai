from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
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
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"DB Startup Warning: {e}")
    yield


app = FastAPI(
    title="InsightForge AI",
    version="1.3.5",
    description="Moteur de personnalisation IA multi-tenant pour SaaS",
    lifespan=lifespan,
)

# Middleware de log pour voir l'origine réelle en cas d'erreur CORS
@app.middleware("http")
async def log_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin:
        print(f"[DEBUG] Request Origin: {origin}")
    response = await call_next(request)
    return response

# CORS : On revient à une liste explicite incluant TOUTES les variantes possibles
origins = [
    "http://localhost:3000",
    "https://frontend-gqaawjux7q-nn.a.run.app",
    "https://frontend-458613429367.northamerica-northeast1.run.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # On force le wildcard car les credentials sont à False
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "env": settings.ENVIRONMENT, "version": "1.3.5"}
