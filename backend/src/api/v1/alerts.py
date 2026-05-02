"""
Endpoint /alerts — Étape 6.
Permet de déclencher manuellement une alerte ou de scanner les users à risque.
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import User
from services.automation.slack_alerts import trigger_churn_alert, CHURN_ALERT_THRESHOLD

router = APIRouter(tags=["Alerts"])


class ManualAlertRequest(BaseModel):
    user_id: str
    churn_score: float
    segment: str = "unknown"


@router.post("/churn")
async def manual_churn_alert(req: ManualAlertRequest):
    """Déclenche manuellement une alerte churn pour un user."""
    result = await trigger_churn_alert(req.user_id, req.churn_score, req.segment)
    return result


@router.post("/scan-churn")
async def scan_and_alert(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Scanne tous les users avec churn_score > seuil et envoie les alertes
    en arrière-plan. Retourne immédiatement le nombre d'users concernés.
    """
    at_risk = (
        db.query(User)
        .filter(User.churn_score >= CHURN_ALERT_THRESHOLD)
        .order_by(User.churn_score.desc())
        .limit(50)
        .all()
    )

    async def _send_all():
        for user in at_risk:
            await trigger_churn_alert(
                user_id=user.user_id,
                churn_score=user.churn_score,
                segment=user.segment or "unknown",
            )

    background_tasks.add_task(_send_all)

    return {
        "status": "scan_started",
        "users_at_risk": len(at_risk),
        "threshold": CHURN_ALERT_THRESHOLD,
        "message": f"{len(at_risk)} alertes en cours d'envoi en arrière-plan.",
    }
