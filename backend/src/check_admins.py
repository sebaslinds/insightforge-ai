import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))
from core.database import SessionLocal
from core.tenant_models import AdminUser, Tenant

db = SessionLocal()
try:
    admins = db.query(AdminUser).all()
    for a in admins:
        t = db.query(Tenant).filter(Tenant.id == a.tenant_id).first()
        print(f"Admin: {a.email} - Tenant: {t.name if t else 'None'} (ID: {a.tenant_id})")
except Exception as e:
    print(f"Erreur: {e}")
finally:
    db.close()
