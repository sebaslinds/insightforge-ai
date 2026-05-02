import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import text
from core.config import get_settings
from sqlalchemy import create_engine

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)

def seed_test_data():
    with engine.connect() as conn:
        print("Nettoyage...")
        conn.execute(text("TRUNCATE TABLE users CASCADE"))
        
        plans = ["free", "pro", "enterprise"]
        segments = ["power_user", "casual", "at_risk", "dormant"]
        countries = ["FR", "US", "UK", "DE", "CA"]
        
        print("Injection de 100 utilisateurs avec toutes les colonnes...")
        for i in range(100):
            user_id = str(uuid.uuid4())
            sc7 = random.randint(0, 50)
            sc30 = sc7 + random.randint(0, 100)
            fb = random.randint(1, 10)
            dur = random.uniform(5, 60)
            ds = random.randint(0, 30)
            eng = random.randint(10, 95)
            churned = True if eng < 30 else False
            churn_score = random.uniform(0, 1)
            
            conn.execute(text("""
                INSERT INTO users (
                    user_id, signup_date, plan, country, segment,
                    session_count_30d, session_count_7d, avg_session_duration_min,
                    feature_breadth, days_since_last_use, engagement_score,
                    churn_score, churned
                ) VALUES (
                    :uid, :now, :plan, :country, :seg,
                    :sc30, :sc7, :dur, :fb, :ds, :eng, :cs, :ch
                )
            """), {
                "uid": user_id, 
                "now": datetime.now() - timedelta(days=random.randint(30, 365)),
                "plan": random.choice(plans),
                "country": random.choice(countries),
                "seg": random.choice(segments),
                "sc30": sc30,
                "sc7": sc7,
                "dur": dur,
                "fb": fb,
                "ds": ds,
                "eng": eng,
                "cs": churn_score,
                "ch": churned
            })
        
        conn.commit()
        print("Seed terminé avec succès ! 100 utilisateurs injectés.")

if __name__ == "__main__":
    seed_test_data()
