import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))
from core.database import SessionLocal
from core.models import User

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Total users: {len(users)}")
    for i, u in enumerate(users):
        print(f"{i+1}: {u.user_id} - Plan: {u.plan} - Tenant: {u.tenant_id}")
except Exception as e:
    print(f"Erreur: {e}")
finally:
    db.close()
