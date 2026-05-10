import os
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from core.tenant_models import Tenant, AdminUser
from core.models import User, Event
from core.security import get_password_hash
from sqlalchemy import text

def seed_cloud():
    print("--- Population massive v7 (Cible 6,000 utilisateurs -> ~600k$) ---")
    
    import core.models
    import core.tenant_models
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.slug == "acme-corp").first()
        if not tenant:
            tenant = Tenant(name="Acme Corporation", slug="acme-corp", plan="enterprise")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

        print("Nettoyage...")
        db.execute(text("DELETE FROM recommendation_feedback"))
        db.execute(text("DELETE FROM events"))
        db.execute(text("DELETE FROM users WHERE tenant_id = :tid"), {"tid": tenant.id})
        db.commit()
        print("Nettoyage OK.")

        segments = ["power_user", "casual", "at_risk", "dormant"]
        plans = ["free", "pro", "enterprise"]
        # Distribution pour atteindre exactement ~594,000$ (99$ ARPU * 6000 users)
        plan_weights = [0.36, 0.49, 0.15]
        
        total_to_add = 6000
        chunk_size = 500
        
        for i in range(0, total_to_add, chunk_size):
            print(f"Chunk {i} à {i+chunk_size}...", flush=True)
            users_chunk = []
            for _ in range(chunk_size):
                profile = random.choice(segments)
                signup_date = datetime.now() - timedelta(days=random.randint(0, 1000))
                
                # Features ML cohérentes
                if profile == "power_user":
                    sessions, breadth, duration, recency, engagement = random.randint(30, 70), random.randint(11, 15), random.uniform(25, 50), random.randint(0, 1), random.uniform(90, 100)
                elif profile == "casual":
                    sessions, breadth, duration, recency, engagement = random.randint(8, 22), random.randint(5, 10), random.uniform(8, 20), random.randint(2, 8), random.uniform(60, 88)
                elif profile == "at_risk":
                    sessions, breadth, duration, recency, engagement = random.randint(1, 6), random.randint(2, 5), random.uniform(2, 7), random.randint(9, 30), random.uniform(30, 55)
                else:
                    sessions, breadth, duration, recency, engagement = 0, random.randint(0, 2), 0, random.randint(31, 150), random.uniform(0, 25)

                plan = random.choices(plans, weights=plan_weights)[0]
                
                users_chunk.append({
                    "user_id": str(uuid.uuid4()),
                    "tenant_id": tenant.id,
                    "signup_date": signup_date,
                    "plan": plan,
                    "segment": profile,
                    "session_count_7d": sessions,
                    "feature_breadth": breadth,
                    "avg_session_duration_min": duration,
                    "days_since_last_use": recency,
                    "engagement_score": engagement,
                    "churn_score": random.uniform(0, 0.15) if profile == "power_user" else random.uniform(0.75, 1.0) if profile in ["at_risk", "dormant"] else random.uniform(0.3, 0.6),
                    "churned": True if profile == "dormant" else (random.random() < 0.45 if profile == "at_risk" else False),
                    "acquisition_channel": random.choice(["google_ads", "linkedin", "organic", "referral", "twitter"]),
                    "acquisition_cost": random.uniform(50, 250) if plan != "free" else 0
                })
            
            db.bulk_insert_mappings(User, users_chunk)
            db.commit()
            print(f"Chunk {i+chunk_size} OK.", flush=True)

        print("--- Population terminée ! ---")
        
    except Exception as e:
        print(f"Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_cloud()
