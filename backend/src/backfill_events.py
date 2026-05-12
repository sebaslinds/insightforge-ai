
import os
import random
from datetime import datetime, timedelta
from core.database import SessionLocal, engine
from core.models import User, Event
from core.tenant_models import Tenant

def backfill_events():
    print("--- Génération massive v3 (db.add + commit par 500) ---", flush=True)
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total users: {len(users)}", flush=True)
        
        events_count = 0
        for idx, user in enumerate(users):
            # Engagement-based sessions
            num_sessions = int(user.engagement_score / 4) + random.randint(3, 10)
            if user.segment == "dormant":
                num_sessions = random.randint(0, 2)
            
            delta_days = (datetime.now() - user.signup_date).days
            for _ in range(num_sessions):
                days_after = random.randint(0, delta_days) if delta_days > 0 else 0
                event_date = user.signup_date + timedelta(days=days_after)
                
                e = Event(
                    user_id=user.user_id,
                    tenant_id=user.tenant_id,
                    event_type="session_start",
                    timestamp=event_date
                )
                db.add(e)
                events_count += 1
                
                if events_count % 500 == 0:
                    db.commit()
                    print(f"  {events_count} events validés...", flush=True)
            
        db.commit()
        print(f"--- Fini ! Total: {events_count} events. ---", flush=True)
        
    except Exception as e:
        print(f"Erreur : {e}", flush=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    backfill_events()
