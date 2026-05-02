"""
Script d'import : lit data/users.csv et data/events.csv et les insère dans PostgreSQL.
Lancement : python data/import_to_db.py
"""
import sys, os
from pathlib import Path

# ── Charger le .env AVANT tout import backend ──────────────────────────────
ROOT = Path(__file__).resolve().parent.parent   # → c:\dev\saas-personalization
ENV_PATH = ROOT / ".env"

from dotenv import load_dotenv
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Debug : vérifier que la variable est bien chargée
db_url = os.getenv("DATABASE_URL", "")
if not db_url:
    print("❌ DATABASE_URL introuvable dans .env — vérifie le fichier !")
    sys.exit(1)
print(f"✅ DATABASE_URL chargée : {db_url[:40]}…")

sys.path.insert(0, str(ROOT / "backend" / "src"))


import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import engine, SessionLocal, Base
from core.models import User, Event

def import_users(db: Session, path: str):
    df = pd.read_csv(path)
    print(f"  → {len(df)} users à importer…")
    batch = []
    for _, row in df.iterrows():
        u = User(
            user_id                  = str(row["user_id"]),
            signup_date              = pd.to_datetime(row["signup_date"]),
            plan                     = row["plan"],
            country                  = row.get("country", None),
            session_count_30d        = int(row["session_count_30d"]),
            session_count_7d         = int(row["session_count_7d"]),
            avg_session_duration_min = float(row["avg_session_duration_min"]),
            feature_breadth          = int(row["feature_breadth"]),
            days_since_last_use      = int(row["days_since_last_use"]),
            engagement_score         = float(row["engagement_score"]),
            churned                  = bool(row["churned"]),
        )
        batch.append(u)
    db.bulk_save_objects(batch)
    db.commit()
    print("  ✅ Users importés.")

def import_events(db: Session, path: str):
    df = pd.read_csv(path)
    print(f"  → {len(df)} events à importer…")
    batch_size = 5000
    for i in range(0, len(df), batch_size):
        chunk = df.iloc[i:i + batch_size]
        batch = []
        for _, row in chunk.iterrows():
            e = Event(
                event_id     = str(row["event_id"]),
                user_id      = str(row["user_id"]),
                timestamp    = pd.to_datetime(row["timestamp"]),
                event_type   = row["event_type"],
                feature_name = row.get("feature_name", None),
                session_id   = str(row["session_id"]),
            )
            batch.append(e)
        db.bulk_save_objects(batch)
        db.commit()
        print(f"    {min(i + batch_size, len(df))}/{len(df)} events…")
    print("  ✅ Events importés.")

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__))
    users_path  = os.path.join(data_dir, "users.csv")
    events_path = os.path.join(data_dir, "events.csv")

    print("🔧 Création des tables…")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées.\n")

    db = SessionLocal()
    try:
        print("📥 Import des users…")
        import_users(db, users_path)
        print("\n📥 Import des events…")
        import_events(db, events_path)
        print("\n🎉 Import complet !")
    finally:
        db.close()
