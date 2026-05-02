import sys
import os
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

# 1. Configurer les chemins pour importer le backend
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend" / "src"))

from core.database import engine, SessionLocal, Base
from core.models import User, Event
from core.tenant_models import Tenant

def import_csv_to_cloud():
    print("--- Importation des CSV vers Cloud SQL ---")
    
    # S'assurer que les tables existent
    import core.models
    import core.tenant_models
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # A. Récupérer ou créer le Tenant par défaut
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

        # B. Importer les Users
        users_path = ROOT / "data" / "users.csv"
        if users_path.exists():
            # Définition des colonnes basées sur generate_users.py
            user_cols = [
                'user_id', 'signup_date', 'plan', 'country', 
                'session_count_30d', 'session_count_7d', 'avg_session_duration_min',
                'feature_breadth', 'days_since_last_use', 'engagement_score', 'churned'
            ]
            
            # On tente de détecter si y'a un header. Si le premier élément commence par "usr_", c'est qu'il n'y a pas de header.
            first_line = pd.read_csv(users_path, nrows=1, header=None)
            has_header = not str(first_line.iloc[0, 0]).startswith("usr_")
            
            if has_header:
                df_users = pd.read_csv(users_path)
            else:
                df_users = pd.read_csv(users_path, names=user_cols, header=None)

            print(f"Analyse de {len(df_users)} utilisateurs...")
            
            user_count = 0
            for _, row in df_users.iterrows():
                uid = str(row["user_id"])
                # Vérifier si l'user existe déjà
                if not db.query(User).filter(User.user_id == uid).first():
                    u = User(
                        user_id=uid,
                        tenant_id=tenant.id,
                        signup_date=pd.to_datetime(row["signup_date"]),
                        plan=str(row["plan"]),
                        country=str(row["country"]),
                        session_count_30d=int(row["session_count_30d"]),
                        session_count_7d=int(row["session_count_7d"]),
                        avg_session_duration_min=float(row["avg_session_duration_min"]),
                        feature_breadth=int(row["feature_breadth"]),
                        days_since_last_use=int(row["days_since_last_use"]),
                        engagement_score=float(row["engagement_score"]),
                        churned=bool(int(row["churned"]))
                    )
                    db.add(u)
                    user_count += 1
                    if user_count % 500 == 0:
                        db.commit()
                        print(f"  ... {user_count} users importés")
            
            db.commit()
            print(f"✅ {user_count} nouveaux utilisateurs importés.")

        # C. Importer les Events
        events_path = ROOT / "data" / "events.csv"
        if events_path.exists():
            df_events = pd.read_csv(events_path) # Possède des headers d'après view_file
            print(f"Importation de {len(df_events)} événements...")
            
            batch_size = 2000
            event_count = 0
            
            for i in range(0, len(df_events), batch_size):
                chunk = df_events.iloc[i : i + batch_size]
                for _, row in chunk.iterrows():
                    e = Event(
                        user_id=str(row["user_id"]),
                        event_type=str(row["event_type"]),
                        feature=str(row["feature_name"]) if pd.notna(row["feature_name"]) else None,
                        timestamp=pd.to_datetime(row["timestamp"])
                    )
                    db.add(e)
                    event_count += 1
                
                db.commit()
                print(f"  {min(i + batch_size, len(df_events))}/{len(df_events)} events...")
            
            print(f"✅ {event_count} événements importés.")

        print("\n🎉 Migration terminée avec succès sur Cloud SQL !")

    except Exception as e:
        print(f"❌ Erreur lors de l'importation : {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import_csv_to_cloud()
