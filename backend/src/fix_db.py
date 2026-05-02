from core.database import engine, SessionLocal
from sqlalchemy import text
from core.tenant_models import Tenant, AdminUser
from core.security import get_password_hash
import uuid

def fix_db():
    print("Nettoyage TOTAL de la base...")
    with engine.connect() as conn:
        # On supprime TOUT par précaution pour le dev
        tables = ["notifications", "business_rules", "events", "users", "admin_users", "api_keys", "tenants"]
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        conn.commit()
    
    # On recrée tout proprement
    from core.database import Base
    import core.models
    import core.tenant_models
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Création du Tenant Acme
        tenant = Tenant(name="Acme Corporation", slug="acme-corp", plan="enterprise")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        print(f"Tenant créé : {tenant.slug}")

        # Création de l'Admin
        admin = AdminUser(
            email="admin@acme.com",
            password_hash=get_password_hash("admin123"),
            full_name="InsightForge Admin",
            tenant_id=tenant.id
        )
        db.add(admin)
        db.commit()
        print("Admin créé : admin@acme.com / admin123")
    finally:
        db.close()

if __name__ == "__main__":
    fix_db()
