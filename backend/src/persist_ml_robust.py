
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))
from core.database import SessionLocal
from services.ml.predictor import _load_models, FEATURE_COLS
from services.ml.feature_engineering import load_features_from_db
import pandas as pd
from sqlalchemy import text

def persist_ml_results():
    print("Loading models and data...")
    xgb, kmeans, scaler = _load_models()
    df = load_features_from_db()
    for col in FEATURE_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['plan_encoded'] = df['plan'].map({'free': 0, 'pro': 1, 'enterprise': 2}).fillna(0)

    print("Predicting...")
    X_scaled = scaler.transform(df[FEATURE_COLS])
    df["cluster"] = kmeans.predict(X_scaled)
    cluster_stats = df.groupby("cluster")["engagement_score"].mean().sort_values(ascending=False)
    dynamic_map = {cluster_id: name for cluster_id, name in zip(cluster_stats.index, ["power_user", "casual", "at_risk", "dormant"])}
    df["segment_name"] = df["cluster"].map(dynamic_map)
    df["churn_score"] = xgb.predict_proba(df[FEATURE_COLS + ["plan_encoded"]])[:, 1]

    print("Bulk updating...")
    db = SessionLocal()
    try:
        # Update 1000 users at a time using CASE or temp table logic
        # For simplicity, we'll use small batches of 200
        batch_size = 200
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            for _, row in batch.iterrows():
                db.execute(text("UPDATE users SET segment = :seg, churn_score = :churn WHERE user_id = :uid"),
                           {"seg": row['segment_name'], "churn": float(row['churn_score']), "uid": row['user_id']})
            db.commit()
            print(f"  - {i+len(batch)} users updated.")
        print("SUCCESS")
    finally:
        db.close()

if __name__ == "__main__": persist_ml_results()
