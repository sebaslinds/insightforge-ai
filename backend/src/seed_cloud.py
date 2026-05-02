import os
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from core.tenant_models import Tenant, AdminUser
from core.models import User, Event
from core.security import get_password_hash

def seed_cloud():
    print("--- Population de la base Cloud SQL ---")
    
    # 1. S'assurer que les tables existent
    import core.models
    import core.tenant_models
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 2. Création du Tenant
        tenant = db.query(Tenant).filter(Tenant.slug == "acme-corp").first()
        if not tenant:
            tenant = Tenant(
                name="Acme Corporation",
                slug="acme-corp",
                plan="enterprise"
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            print(f"Tenant créé : {tenant.name}")
        else:
            print(f"Tenant existant : {tenant.name}")

        # 3. Création ou mise à jour de l'Admin
        admin = db.query(AdminUser).filter(AdminUser.email == "admin@acme.com").first()
        if not admin:
            admin = AdminUser(
                email="admin@acme.com",
                password_hash=get_password_hash("admin123"),
                full_name="InsightForge Admin",
                tenant_id=tenant.id
            )
            db.add(admin)
            print("Admin créé : admin@acme.com / admin123")
        else:
            admin.tenant_id = tenant.id
            db.add(admin)
            print("Admin existant rattaché au tenant Acme.")

        # 4. Génération d'utilisateurs réalistes (Cohortes 12 semaines)
        print("Génération de cohortes sur les 12 dernières semaines...")
        segments = ["power_user", "casual", "at_risk", "dormant"]
        plans = ["pro", "enterprise"] # On se concentre sur les payants pour la démo
        
        for w in range(12, -1, -1):
            cohort_date = datetime.now() - timedelta(weeks=w)
            num_users_in_cohort = random.randint(15, 30)
            
            for _ in range(num_users_in_cohort):
                profile = random.choice(segments)
                # Date d'inscription précise dans la semaine
                signup_date = cohort_date + timedelta(days=random.randint(0, 6))
                
                user = User(
                    user_id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    signup_date=signup_date,
                    plan=random.choice(plans),
                    segment=profile,
                    engagement_score=random.uniform(40, 95) if profile != "dormant" else random.uniform(5, 20),
                    churn_score=random.uniform(0, 0.3) if profile == "power_user" else random.uniform(0.7, 0.95)
                )
                db.add(user)
                
                # Générer des événements de "Rétention"
                # Plus le temps passe (week_idx élevé), moins il y a de chances de retour
                for week_idx in range(w + 1):
                    # Probabilité de retour basée sur le segment et l'ancienneté
                    retention_prob = 0.9 if week_idx == 0 else 0.7 if profile == "power_user" else 0.3
                    # La rétention baisse avec le temps (decay)
                    retention_prob = retention_prob * (0.95 ** week_idx)
                    
                    if random.random() < retention_prob:
                        # L'utilisateur est revenu cette semaine-là
                        event_date = signup_date + timedelta(weeks=week_idx, days=random.randint(0, 6))
                        if event_date <= datetime.now():
                            event = Event(
                                user_id=user.user_id,
                                tenant_id=tenant.id,
                                event_type="session_start",
                                timestamp=event_date
                            )
                            db.add(event)

        db.commit()
        print("--- Migration et population terminées avec succès ! ---")
        
    except Exception as e:
        print(f"Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_cloud()
