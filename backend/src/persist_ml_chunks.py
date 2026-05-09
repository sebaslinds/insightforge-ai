
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))
from core.database import SessionLocal
from core.models import User
from core.tenant_models import Tenant
from services.ml.predictor import _load_models, FEATURE_COLS
from services.ml.feature_engineering import load_features_from_db
import pandas as pd

def persist_ml_results():
    print("Loading models...")
    xgb, kmeans, scaler = _load_models()
    print("Loading features...")
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

    print("Updating in chunks...")
    db = SessionLocal()
    try:
        count = 0
        for _, row in df.iterrows():
            db.execute(text("UPDATE users SET segment = :seg, churn_score = :churn WHERE user_id = :uid"), 
                       {"seg": row['segment_name'], "churn": float(row['churn_score']), "uid": row['user_id']})
            count += 1
            if count % 500 == 0:
                db.commit()
                print(f"  - {count} users committed.")
        db.commit()
        print(f"SUCCESS: {count} users updated.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

from sqlalchemy import text
if __name__ == "__main__": persist_ml_results()
