import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))
from core.database import SessionLocal
from core.models import User
from core.tenant_models import AdminUser
import pandas as pd

db = SessionLocal()
try:
    admin = db.query(AdminUser).filter(AdminUser.email == "admin@acme.com").first()
    tenant_id = admin.tenant_id
    
    PLAN_PRICES = {"free": 0, "pro": 49, "enterprise": 499}
    users = db.query(User).filter(User.tenant_id == tenant_id).all()
    
    df = pd.DataFrame([{
        "plan": u.plan, 
        "engagement_score": u.engagement_score, 
        "churned": u.churned
    } for u in users])
    
    total_revenue = sum(df['plan'].map(PLAN_PRICES).fillna(0))
    active_users = len(df)
    
    print(f"Tenant ID: {tenant_id}")
    print(f"Users found: {active_users}")
    print(f"Total Revenue: ${total_revenue}")
    
except Exception as e:
    print(f"Erreur: {e}")
finally:
    db.close()
