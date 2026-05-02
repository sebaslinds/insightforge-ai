from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from core.database import get_db
from core.tenant_models import ApiKey, Tenant
from core.models import Event, User

router = APIRouter()

class EventSchema(BaseModel):
    user_id: str
    event_type: str
    feature: Optional[str] = None
    properties: Optional[dict] = None

async def verify_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    """Valide la clé API et retourne le Tenant associé."""
    key_entry = db.query(ApiKey).filter(ApiKey.key == x_api_key, ApiKey.is_active == True).first()
    if not key_entry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou inactive"
        )
    
    # Update last_used_at
    key_entry.last_used_at = datetime.utcnow()
    db.commit()
    
    return key_entry.tenant_id

@router.post("/")
async def capture_event(
    event: EventSchema,
    tenant_id: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Module 1 : Capture d'événements brute.
    """
    # 1. On vérifie si l'utilisateur existe pour ce tenant, sinon on le crée (simplifié)
    user = db.query(User).filter(User.user_id == event.user_id).first()
    if not user:
        # Création auto de l'utilisateur s'il n'existe pas encore dans notre système
        user = User(
            user_id=event.user_id,
            tenant_id=tenant_id,
            signup_date=datetime.utcnow(),
            plan="free" # Par défaut
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Enregistrement de l'événement
    db_event = Event(
        user_id=event.user_id,
        event_type=event.event_type,
        feature=event.feature,
        timestamp=datetime.utcnow()
    )
    db.add(db_event)

    # 3. Logique spécifique (ex: conversion change le plan)
    if event.event_type == "conversion" and event.feature:
        user.plan = event.feature
        print(f"[Events] User {user.user_id} converted to plan: {event.feature}")

    db.commit()

    return {"status": "success", "event_id": db_event.id}
