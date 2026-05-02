from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from core.tenant_models import AdminUser, Tenant
from core.security import verify_password, create_access_token, get_password_hash

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "tenant_id": str(user.tenant_id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/setup-first-user")
def setup_first_user(db: Session = Depends(get_db)):
    """Endpoint temporaire pour créer le premier utilisateur de démo."""
    """Endpoint temporaire pour créer ou réinitialiser le premier utilisateur de démo."""
    # On vérifie si un tenant existe, sinon on le crée
    tenant = db.query(Tenant).filter(Tenant.slug == "acme-corp").first()
    if not tenant:
        tenant = Tenant(name="Acme Corporation", slug="acme-corp", plan="enterprise")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    # Création ou réinitialisation de l'admin par défaut
    admin_email = "admin@acme.com"
    existing = db.query(AdminUser).filter(AdminUser.email == admin_email).first()
    
    if existing:
        existing.password_hash = get_password_hash("admin123")
        db.commit()
        return {"message": "Admin mis à jour : admin@acme.com / admin123"}
    
    new_admin = AdminUser(
        email=admin_email,
        password_hash=get_password_hash("admin123"),
        full_name="InsightForge Admin",
        tenant_id=tenant.id
    )
    db.add(new_admin)
    db.commit()
    return {"message": "Admin créé : admin@acme.com / admin123"}
