
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
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
        # Fallback local
        return pg8000.connect(
            user=DB_USER,
            password=DB_PASS,
            host="localhost",
            port=5432,
            database=DB_NAME
        )

def generate_extra_users(count=1000, tenant_id=None):
    print(f"--- Generation de {count} utilisateurs (2024-2026) ---")
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 5, 1)
    
    users = []
    for _ in range(count):
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        # Date aléatoire entre 2024 et 2026
        days_diff = (end_date - start_date).days
        signup_date = start_date + timedelta(days=np.random.randint(0, days_diff))
        
        plan = np.random.choice(['free', 'pro', 'enterprise'], p=[0.7, 0.25, 0.05])
        churned = 1 if np.random.random() < 0.15 else 0
        engagement = np.random.randint(10, 95)
        
        users.append({
            "user_id": user_id,
            "signup_date": signup_date,
            "plan": plan,
            "country": np.random.choice(['FR', 'US', 'UK', 'CA', 'DE']),
            "session_count_30d": np.random.randint(0, 50),
            "session_count_7d": np.random.randint(0, 15),
            "avg_session_duration_min": round(np.random.uniform(1.0, 20.0), 1),
            "feature_breadth": np.random.randint(0, 6),
            "days_since_last_use": np.random.randint(0, 30),
            "engagement_score": engagement,
            "churned": churned,
            "tenant_id": tenant_id
        })
    
    return pd.DataFrame(users)

def main():
    # 0. Récupérer le tenant_id
    print("START: Recuperation du tenant_id...")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tenants LIMIT 1")
    res = cursor.fetchone()
    if not res:
        print("ERROR: Aucun tenant trouve en base.")
        conn.close()
        return
    tenant_id = res[0]
    print(f"OK: Utilisation du tenant {tenant_id}")
    
    df = generate_extra_users(1000, tenant_id=tenant_id)
    
    # 1. Sauvegarde locale (append)
    csv_path = "data/users.csv"
    df.to_csv(csv_path, mode='a', header=False, index=False)
    print(f"OK: {len(df)} users ajoutes a {csv_path}")
    
    # 2. Injection Cloud SQL
    print("START: Injection vers Cloud SQL...")
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Préparation des données pour execute_many
        data_to_insert = []
        for idx, row in df.iterrows():
            data_to_insert.append((
                row['user_id'], row['signup_date'], row['plan'], row['country'], 
                row['session_count_30d'], row['session_count_7d'], row['avg_session_duration_min'], 
                row['feature_breadth'], row['days_since_last_use'], row['engagement_score'], 
                row['churned'], row['tenant_id']
            ))
            
        cursor.executemany(
            "INSERT INTO users (user_id, signup_date, plan, country, session_count_30d, session_count_7d, avg_session_duration_min, feature_breadth, days_since_last_use, engagement_score, churned, tenant_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            data_to_insert
        )
        conn.commit()
        print("OK: Injection reussie !")
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
