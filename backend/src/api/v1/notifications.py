from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.models import Notification, BusinessRule
from core.tenant_models import AdminUser
from core.security import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("")
def get_notifications(current_user: AdminUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.tenant_id == current_user.tenant_id).order_by(Notification.created_at.desc()).limit(20).all()

@router.post("/{notif_id}/read")
def mark_read(notif_id: int, current_user: AdminUser = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.tenant_id == current_user.tenant_id).first()
    if notif:
        notif.read = True
        db.commit()
    return {"status": "ok"}

@router.post("/trigger-demo")
def trigger_demo_notifications(current_user: AdminUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # Clear old notifications to keep the demo clean and avoid huge history
    db.query(Notification).filter(Notification.tenant_id == current_user.tenant_id).delete()

    # Simule le moteur de décision qui s'active
    rules = db.query(BusinessRule).filter(BusinessRule.tenant_id == current_user.tenant_id, BusinessRule.enabled == True).all()
    
    new_notifs = []
    for rule in rules:
        notif = Notification(
            tenant_id=current_user.tenant_id,
            title=f"Rule Triggered: {rule.name}",
            message=f"InsightForge automation executed: {rule.description[:50]}...",
            type="success" if "Automation" in rule.name else "info"
        )
        db.add(notif)
        new_notifs.append(notif)
    
    db.commit()
    return {"status": "triggered", "count": len(new_notifs)}

@router.delete("")
@router.delete("/")
def clear_notifications(current_user: AdminUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Supprime toutes les notifications du tenant."""
    print(f"DEBUG: clear_notifications hit for user {current_user.email}")
    db.query(Notification).filter(Notification.tenant_id == current_user.tenant_id).delete()
    db.commit()
    return {"status": "ok"}
