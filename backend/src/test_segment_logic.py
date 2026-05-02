
import pandas as pd
import numpy as np

# Mocking SEGMENT_MAP and dummy data
SEGMENT_MAP = {0: "power_user", 1: "casual", 2: "at_risk", 3: "dormant"}

def get_segments_mock():
    # Mocking df from load_features_from_db
    df = pd.DataFrame({
        "user_id": range(100),
        "engagement_score": np.random.randint(0, 100, 100),
        "days_since_last_use": np.random.randint(0, 30, 100),
        "segment": [None] * 100 # Initial segment column from DB
    })
    
    # Mocking labels from kmeans.predict
    labels = np.random.randint(0, 4, 100)
    
    # Logic from predictor.py
    df["segment"] = [SEGMENT_MAP[l] for l in labels]
    
    summary = df.groupby("segment").agg(
        count=("user_id", "count"),
        avg_score=("engagement_score", "mean"),
        avg_churn_days=("days_since_last_use", "mean"),
    ).reset_index()
    
    total_users = summary["count"].sum()
    summary["percentage"] = (summary["count"] / total_users) * 100
    summary = summary.rename(columns={"segment": "name"})
    
    return summary.to_dict(orient="records")

if __name__ == "__main__":
    res = get_segments_mock()
    import json
    print(json.dumps(res, indent=2))
