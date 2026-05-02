import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))
from core.database import SessionLocal
from core.models import User

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Total users in DB: {len(users)}")
    tenants = {}
    for u in users:
        tenants[u.tenant_id] = tenants.get(u.tenant_id, 0) + 1
    for t_id, count in tenants.items():
        print(f"Tenant ID {t_id}: {count} users")
except Exception as e:
    print(f"Erreur: {e}")
finally:
    db.close()
