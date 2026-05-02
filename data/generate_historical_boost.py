
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
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
    print("START: Boost historique (2023-2025)...")
    conn = get_connection()
    cursor = conn.cursor()
    
    # 0. Récupérer le tenant_id
    cursor.execute("SELECT id FROM tenants LIMIT 1")
    tenant_id = cursor.fetchone()[0]
    
    # 1. Générer 500 utilisateurs en 2023
    print("--- Creation de 500 utilisateurs (2023) ---")
    start_2023 = datetime(2023, 1, 1)
    end_2023 = datetime(2023, 12, 31)
    
    new_users = []
    for _ in range(500):
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        days_diff = (end_2023 - start_2023).days
        signup_date = start_2023 + timedelta(days=np.random.randint(0, days_diff))
        
        plan = np.random.choice(['pro', 'enterprise', 'free'], p=[0.4, 0.1, 0.5]) # Plus de payants pour booster le revenu
        new_users.append((user_id, signup_date, plan, 'FR', tenant_id))

    # Insertion des users
    cursor.executemany(
        "INSERT INTO users (user_id, signup_date, plan, country, churned, tenant_id) VALUES (%s, %s, %s, %s, False, %s)",
        new_users
    )
    conn.commit()
    print(f"OK: 500 nouveaux utilisateurs inseres pour 2023.")

    # 2. Générer des événements pour 2023-2025
    print("--- Generation d'evenements (2023-2025) ---")
    cursor.execute("SELECT user_id, signup_date FROM users WHERE signup_date < '2026-01-01'")
    historical_users = cursor.fetchall()
    
    events = []
    features_list = ["Analytics", "Copilot", "Segments", "Decision Engine"]
    
    for user_id, signup_date in historical_users:
        # Entre 20 et 60 evenements sur la periode
        num_events = np.random.randint(20, 60)
        
        for _ in range(num_events):
            # Date aleatoire entre signup et fin 2025
            limit_date = datetime(2025, 12, 31)
            days_diff = (limit_date - signup_date).days
            if days_diff <= 0: continue
            
            event_date = signup_date + timedelta(days=np.random.randint(0, days_diff), seconds=np.random.randint(0, 86400))
            
            etype = np.random.choice(["page_view", "feature_use", "session_start"], p=[0.3, 0.5, 0.2])
            feature = np.random.choice(features_list) if etype == "feature_use" else None
            
            events.append((user_id, etype, feature, event_date))
            
            if len(events) >= 5000:
                # Utilisation de la methode rapide (multi-row insert)
                placeholders = []
                params = []
                for row in events:
                    placeholders.append("(%s, %s, %s, %s)")
                    params.extend(row)
                query = f"INSERT INTO events (user_id, event_type, feature, timestamp) VALUES {', '.join(placeholders)}"
                cursor.execute(query, params)
                conn.commit()
                events = []

    if events:
        placeholders = []
        params = []
        for row in events:
            placeholders.append("(%s, %s, %s, %s)")
            params.extend(row)
        query = f"INSERT INTO events (user_id, event_type, feature, timestamp) VALUES {', '.join(placeholders)}"
        cursor.execute(query, params)
        conn.commit()

    print(f"OK: Boost historique termine.")
    conn.close()

if __name__ == "__main__":
    main()
