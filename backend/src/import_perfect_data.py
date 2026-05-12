import pandas as pd
from sqlalchemy import text
from core.database import SessionLocal
from core.models import User

def import_perfect_data():
    df = pd.read_csv('perfect_users.csv')
    db = SessionLocal()
    try:
        print("[IMPORT] Truncating users table...")
        db.execute(text("TRUNCATE TABLE users CASCADE;"))
        db.commit()
        
        print(f"[IMPORT] Inserting {len(df)} users...")
        tenant_id = "b205c3d4-3a6a-409b-9000-01dca0af7745"
        users = []
        for _, row in df.iterrows():
            user = User(
                user_id=row['user_id'],
                tenant_id=tenant_id,
                session_count_7d=row['session_count_7d'],
                feature_breadth=row['feature_breadth'],
                avg_session_duration_min=row['avg_session_duration_min'],
                days_since_last_use=row['days_since_last_use'],
                engagement_score=row['engagement_score'],
                churned=bool(row['churned']),
                plan=row['plan'],
                segment=row['segment'],
                churn_score=0.0 # Will be updated by trainer
            )
            users.append(user)
            
            if len(users) >= 500:
                db.bulk_save_objects(users)
                db.commit()
                users = []
                print(f"  - {_+1} users imported...")
        
        if users:
            db.bulk_save_objects(users)
            db.commit()
            
        print("[OK] Import successful.")
    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_perfect_data()
