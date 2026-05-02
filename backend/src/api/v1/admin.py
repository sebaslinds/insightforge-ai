"""
Endpoint d'administration des tenants et API Keys.
Préfixe : /admin  (à ne pas exposer en production sans auth admin séparée)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from core.tenant_models import ApiKey, Tenant
from core.security import generate_api_key

router = APIRouter(tags=["Admin"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class TenantCreate(BaseModel):
    name: str
    slug: str
    plan: str = "free"


class TenantOut(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    is_active: bool

    class Config:
        from_attributes = True


class ApiKeyOut(BaseModel):
    id: str
    key: str
    label: str | None
    tenant_id: str
    is_active: bool

    class Config:
        from_attributes = True


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/tenants", response_model=TenantOut, status_code=201)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    """Crée un nouveau tenant SaaS."""
    if db.query(Tenant).filter(Tenant.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail=f"Slug '{payload.slug}' déjà utilisé.")
    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    # Sérialise l'UUID en string
    tenant.id = str(tenant.id)
    return tenant


@router.get("/tenants", response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db)):
    """Liste tous les tenants."""
    tenants = db.query(Tenant).all()
    for t in tenants:
        t.id = str(t.id)
    return tenants


@router.post("/tenants/{tenant_slug}/api-keys", response_model=ApiKeyOut, status_code=201)
def create_api_key(
    tenant_slug: str,
    label: str = "Default Key",
    db: Session = Depends(get_db),
):
    """Génère une API Key pour un tenant."""
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant introuvable.")

    raw_key = generate_api_key()
    api_key = ApiKey(tenant_id=tenant.id, key=raw_key, label=label)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return ApiKeyOut(
        id=str(api_key.id),
        key=api_key.key,
        label=api_key.label,
        tenant_id=str(api_key.tenant_id),
        is_active=api_key.is_active,
    )


@router.delete("/api-keys/{key_id}", status_code=204)
def revoke_api_key(key_id: str, db: Session = Depends(get_db)):
    """Révoque (désactive) une API Key."""
    record = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="API Key introuvable.")
    record.is_active = False
    db.commit()
