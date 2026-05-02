
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from sqlalchemy import create_engine, text
from google.cloud.sql.connector import Connector
import pg8000
from dotenv import load_dotenv

# Charger le .env
load_dotenv()

# Configuration
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME", "insightforge")
INSTANCE_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")

def get_connection():
    if INSTANCE_NAME:
        connector = Connector()
        return connector.connect(
            INSTANCE_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME
        )
    else:
        return pg8000.connect(
            user=DB_USER,
            password=DB_PASS,
            host="localhost",
            port=5432,
            database=DB_NAME
        )

def main():
    print("START: Generation d'evenements historiques...")
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Recuperer tous les users du tenant Acme Corp
    cursor.execute("SELECT user_id, signup_date, engagement_score FROM users")
    users = cursor.fetchall()
    print(f"OK: {len(users)} utilisateurs trouves.")
    
    now = datetime.now()
    events = []
    
    features_list = ["Analytics", "Copilot", "Segments", "Decision Engine", "Project Info", "Settings"]
    
    for user_id, signup_date, engagement in users:
        # Nombre d'evenements proportionnel a l'engagement
        num_events = int(np.random.normal(engagement * 0.8, 10))
        num_events = max(5, num_events) # Au moins 5
        
        for _ in range(num_events):
            # Date aleatoire entre signup et aujourd'hui
            days_diff = (now - signup_date).days
            if days_diff <= 0:
                event_date = signup_date
            else:
                event_date = signup_date + timedelta(days=np.random.randint(0, days_diff), seconds=np.random.randint(0, 86400))
            
            # Type d'evenement
            etype = np.random.choice(["page_view", "feature_use", "session_start"], p=[0.4, 0.4, 0.2])
            feature = None
            if etype == "feature_use":
                feature = np.random.choice(features_list)
            
            events.append((user_id, etype, feature, event_date))
            
            # Bulk insert tous les 5000 evenements
            if len(events) >= 5000:
                print(f"PROGRESS: Insertion de {len(events)} evenements...")
                cursor.executemany(
                    "INSERT INTO events (user_id, event_type, feature, timestamp) VALUES (%s, %s, %s, %s)",
                    events
                )
                conn.commit()
                events = []

    # Dernier batch
    if events:
        print(f"FINISH: Insertion des {len(events)} derniers evenements...")
        cursor.executemany(
            "INSERT INTO events (user_id, event_type, feature, timestamp) VALUES (%s, %s, %s, %s)",
            events
        )
        conn.commit()

    print("OK: Tous les evenements ont ete generes et inseres.")
    conn.close()

if __name__ == "__main__":
    main()
