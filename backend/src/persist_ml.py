
import sys
import os
from pathlib import Path

# Setup paths
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))

from core.database import SessionLocal
from core.models import User
from services.ml.predictor import _load_models, FEATURE_COLS
from services.ml.feature_engineering import load_features_from_db
import pandas as pd
import numpy as np

def persist_ml_results():
    print("[Persistence] Loading models and data...")
    try:
        xgb, kmeans, scaler = _load_models()
    except Exception as e:
        print(f"Error loading models: {e}")
        return

    df = load_features_from_db()
    if df.empty:
        print("No users found in database.")
        return

    print(f"[Persistence] Processing {len(df)} users...")

    # Preprocessing
    for col in FEATURE_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # plan_encoded logic (from predictor or trainer)
    df['plan_encoded'] = df['plan'].map({'free': 0, 'pro': 1, 'enterprise': 2}).fillna(0)

    # 1. Segments (K-Means)
    X_scaled = scaler.transform(df[FEATURE_COLS])
    df["cluster"] = kmeans.predict(X_scaled)
    
    # Dynamic Mapping (logic from predictor.py)
    cluster_stats = df.groupby("cluster")["engagement_score"].mean().sort_values(ascending=False)
    dynamic_map = {}
    names = ["power_user", "casual", "at_risk", "dormant"]
    for i, cluster_id in enumerate(cluster_stats.index):
        if i < len(names):
            dynamic_map[cluster_id] = names[i]
        else:
            dynamic_map[cluster_id] = f"cluster_{cluster_id}"
    
    df["segment_name"] = df["cluster"].map(dynamic_map)

    # 2. Churn Scores (XGBoost)
    X_xgb = df[FEATURE_COLS + ["plan_encoded"]]
    df["churn_score"] = xgb.predict_proba(X_xgb)[:, 1]

    # 3. Update Database
    db = SessionLocal()
    try:
        print("[Persistence] Updating database...")
        updated = 0
        for _, row in df.iterrows():
            user = db.query(User).filter(User.user_id == row['user_id']).first()
            if user:
                user.segment = row['segment_name']
                user.churn_score = float(row['churn_score'])
                updated += 1
                if updated % 1000 == 0:
                    print(f"  - {updated} users updated...")
        
        db.commit()
        print(f"[Persistence] SUCCESS: {updated} users updated in DB.")
    except Exception as e:
        print(f"Error during DB update: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    persist_ml_results()
