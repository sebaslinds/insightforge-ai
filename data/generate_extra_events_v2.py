
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import pg8000
from google.cloud.sql.connector import Connector
from dotenv import load_dotenv

# Charger le .env et nettoyer l'environnement
load_dotenv()
os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)

# Configuration
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS").strip('"') if os.getenv("DB_PASS") else ""
DB_NAME = os.getenv("DB_NAME", "insightforge")
INSTANCE_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")

def get_connection():
    connector = Connector()
    return connector.connect(
        INSTANCE_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )

def main():
    print("START: Generation d'evenements historiques...")
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Recuperer les users qui n'ont pas encore d'evenements (ou juste les nouveaux)
    # Pour faire simple, on en prend 1000 au hasard pour simuler une activite globale
    cursor.execute("SELECT user_id, signup_date, engagement_score FROM users ORDER BY signup_date DESC LIMIT 1500")
    users = cursor.fetchall()
    print(f"OK: {len(users)} utilisateurs selectionnes pour simulation.")
    
    now = datetime.now()
    all_events = []
    features_list = ["Analytics", "Copilot", "Segments", "Decision Engine", "Project Info", "Settings"]
    
    for user_id, signup_date, engagement in users:
        # Entre 10 et 40 evenements par user
        num_events = np.random.randint(10, 40)
        
        for _ in range(num_events):
            days_diff = (now - signup_date).days
            if days_diff <= 0:
                event_date = signup_date
            else:
                event_date = signup_date + timedelta(days=np.random.randint(0, days_diff), seconds=np.random.randint(0, 86400))
            
            etype = np.random.choice(["page_view", "feature_use", "session_start"], p=[0.4, 0.4, 0.2])
            feature = np.random.choice(features_list) if etype == "feature_use" else None
            
            all_events.append((user_id, etype, feature, event_date))

    # 2. Insertion groupée (Batch de 500)
    batch_size = 500
    for i in range(0, len(all_events), batch_size):
        batch = all_events[i : i + batch_size]
        print(f"PROGRESS: Insertion du batch {i//batch_size + 1} ({len(batch)} rows)...", flush=True)
        
        # Construction de la requête manuelle
        placeholders = []
        params = []
        for row in batch:
            placeholders.append("(%s, %s, %s, %s)")
            params.extend(row)
        
        query = f"INSERT INTO events (user_id, event_type, feature, timestamp) VALUES {', '.join(placeholders)}"
        cursor.execute(query, params)
        conn.commit()

    print(f"OK: {len(all_events)} evenements inseres.")
    conn.close()

if __name__ == "__main__":
    main()
