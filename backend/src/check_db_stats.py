import sys
import os

# Ajout du chemin backend/src au python path
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))

from core.database import SessionLocal
from core.models import User
from core.tenant_models import Tenant, AdminUser

db = SessionLocal()
try:
    tenant = db.query(Tenant).filter(Tenant.slug == "acme-corp").first()
    if not tenant:
        print("Tenant 'acme-corp' non trouvé.")
    else:
        users = db.query(User).filter(User.tenant_id == tenant.id).all()
        print(f"Tenant: {tenant.name} (ID: {tenant.id})")
        print(f"Nombre d'utilisateurs: {len(users)}")
        
        plans_count = {}
        for u in users:
            plans_count[u.plan] = plans_count.get(u.plan, 0) + 1
        
        print("Plans:")
        for plan, count in plans_count.items():
            print(f"  - {plan}: {count}")
        
        PLAN_PRICES = {"free": 0, "pro": 49, "enterprise": 499}
        total_rev = sum(PLAN_PRICES.get(u.plan, 0) for u in users)
        print(f"Revenu calculé: ${total_rev}")

except Exception as e:
    print(f"Erreur: {e}")
finally:
    db.close()
