from fastapi import APIRouter
from .ask import router as ask_router
from .decision import router as decision_router
from .ml import router as ml_router
from .admin import router as admin_router
from .alerts import router as alerts_router
from .analytics import router as analytics_router
from .auth import router as auth_router
from .notifications import router as notifications_router
from .events import router as events_router

api_router = APIRouter()
api_router.include_router(auth_router,      prefix="/auth",      tags=["Auth"])
api_router.include_router(events_router,    prefix="/events",    tags=["Tracking"])
api_router.include_router(ask_router,      prefix="/ask",      tags=["Copilot"])
api_router.include_router(decision_router, prefix="/decision", tags=["Decision"])
api_router.include_router(ml_router,       prefix="/ml",       tags=["ML"])
api_router.include_router(admin_router,    prefix="/admin",    tags=["Admin"])
api_router.include_router(alerts_router,   prefix="/alerts",   tags=["Alerts"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
