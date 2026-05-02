from fastapi import APIRouter
from .ask import router as ask_router
from .decision import router as decision_router
from .ml import router as ml_router
from .admin import router as admin_router
from .alerts import router as alerts_router

api_router = APIRouter()
api_router.include_router(ask_router,      prefix="/ask",      tags=["Copilot"])
api_router.include_router(decision_router, prefix="/decision", tags=["Decision"])
api_router.include_router(ml_router,       prefix="/ml",       tags=["ML"])
api_router.include_router(admin_router,    prefix="/admin",    tags=["Admin"])
api_router.include_router(alerts_router,   prefix="/alerts",   tags=["Alerts"])
