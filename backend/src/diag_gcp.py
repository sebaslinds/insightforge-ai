import sys
import os
from datetime import datetime, timedelta

# Ajouter src au path
sys.path.append(os.path.join(os.getcwd(), "backend/src"))

from core.database import SessionLocal
from core.models import User, Event
from core.tenant_models import Tenant, AdminUser

def diag():
    db = SessionLocal()
    try:
        print("--- Diagnostic InsightForge AI (GCP) ---")
        
        # 1. Vérifier le tenant
        tenant = db.query(Tenant).filter(Tenant.slug == "acme-corp").first()
        if not tenant:
            print("ERREUR : Tenant acme-corp introuvable.")
            return
        print(f"Tenant OK : {tenant.name} ({tenant.id})")

        # 2. Vérifier l'admin
        admin = db.query(AdminUser).filter(AdminUser.email == "admin@acme.com").first()
        if not admin:
            print("ERREUR : Admin admin@acme.com introuvable.")
        else:
            print(f"Admin OK : {admin.email} (Tenant: {admin.tenant_id})")
            if admin.tenant_id != tenant.id:
                print("!!! ATTENTION : Tenant ID mismatch pour l'admin !!!")

        # 3. Compter les données
        user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
        event_count = db.query(Event).filter(Event.tenant_id == tenant.id).count()
        
        print(f"Utilisateurs (Acme) : {user_count}")
        print(f"Événements (Acme)    : {event_count}")

        # 4. Vérifier les dates
        limit_date = datetime.now() - timedelta(weeks=16)
        recent_users = db.query(User).filter(User.tenant_id == tenant.id, User.signup_date >= limit_date).count()
        print(f"Utilisateurs récents (16w) : {recent_users}")

    finally:
        db.close()

if __name__ == "__main__":
    diag()
