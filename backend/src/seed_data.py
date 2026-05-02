from core.database import SessionLocal
from core.models import User, Event
from core.tenant_models import Tenant
import uuid
from datetime import datetime, timedelta
import random

def seed_users():
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.slug == "acme-corp").first()
        if not tenant:
            print("Tenant non trouvé. Lance fix_db.py d'abord.")
            return

        print(f"Génération de données pour {tenant.name}...")
        
        # On supprime les anciens users du tenant pour éviter les doublons
        db.query(User).filter(User.tenant_id == tenant.id).delete()
        
        plans = ["free", "pro", "enterprise"]
        segments = ["power_user", "casual", "at_risk", "dormant"]
        countries = ["US", "FR", "CA", "DE", "UK"]

        for i in range(1000):
            # Génération sur 3 ans (2023, 2024, 2025, 2026)
            signup_date = datetime.now() - timedelta(days=random.randint(0, 365*3.5))
            plan = random.choices(plans, weights=[50, 40, 10])[0]
            
            # On crée des profils typés pour que le clustering fonctionne
            profile = random.choice(segments)
            
            if profile == "power_user":
                sessions_7d = random.randint(30, 60)
                breadth = random.randint(10, 15)
                duration = random.uniform(20, 45)
                days_since = random.randint(0, 2)
                score = random.uniform(80, 100)
            elif profile == "casual":
                sessions_7d = random.randint(5, 20)
                breadth = random.randint(4, 10)
                duration = random.uniform(10, 25)
                days_since = random.randint(1, 7)
                score = random.uniform(40, 75)
            elif profile == "at_risk":
                sessions_7d = random.randint(1, 10)
                breadth = random.randint(2, 6)
                duration = random.uniform(5, 15)
                days_since = random.randint(5, 14)
                score = random.uniform(20, 50)
            else: # dormant
                sessions_7d = random.randint(0, 2)
                breadth = random.randint(1, 4)
                duration = random.uniform(1, 10)
                days_since = random.randint(15, 30)
                score = random.uniform(0, 25)

            user = User(
                user_id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                signup_date=signup_date,
                plan=plan,
                country=random.choice(countries),
                segment=profile,
                session_count_30d=sessions_7d * 4 + random.randint(0, 20),
                session_count_7d=sessions_7d,
                feature_breadth=breadth,
                avg_session_duration_min=duration,
                days_since_last_use=days_since,
                engagement_score=score,
                churn_score=1.0 - (score / 100.0),
                churned=(score < 20 and random.random() < 0.7)
            )
            db.add(user)
            
            # Génération d'événements pour le moteur de recommandation
            features_pool = ["dashboard", "analytics", "reports", "settings", "copilot", "ml_train", "api_export", "alerts_config", "tenant_admin"]
            # Les power users utilisent plus de features
            num_events = random.randint(20, 50) if profile == "power_user" else random.randint(5, 15)
            used_features = random.sample(features_pool, random.randint(3, len(features_pool)) if profile == "power_user" else random.randint(1, 4))
            
            for _ in range(num_events):
                event = Event(
                    user_id=user.user_id,
                    event_type="feature_use",
                    feature=random.choice(used_features),
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
                )
                db.add(event)
        
        db.commit()
        print("100 utilisateurs générés avec succès (clusters réalistes) !")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
