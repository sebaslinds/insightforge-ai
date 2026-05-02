import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))
from core.database import SessionLocal
from core.tenant_models import Tenant, AdminUser
from core.models import User

db = SessionLocal()
try:
    tenants = db.query(Tenant).all()
    print(f"Nombre de tenants: {len(tenants)}")
    for t in tenants:
        admin = db.query(AdminUser).filter(AdminUser.tenant_id == t.id).first()
        users_count = db.query(User).filter(User.tenant_id == t.id).count()
        print(f"Tenant: {t.name} (Slug: {t.slug}) - Users: {users_count} - Admin: {admin.email if admin else 'None'}")
except Exception as e:
    print(f"Erreur: {e}")
finally:
    db.close()
