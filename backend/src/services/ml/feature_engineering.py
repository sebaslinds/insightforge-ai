"""
Feature Engineering : lit la table users depuis PostgreSQL et retourne un DataFrame ML-ready.
"""
import pandas as pd
from sqlalchemy import text
from core.database import SessionLocal

FEATURE_COLS = [
    "session_count_7d",
    "feature_breadth",
    "avg_session_duration_min",
    "days_since_last_use",
    "engagement_score",
]

def load_features_from_db() -> pd.DataFrame:
    """Retourne un DataFrame avec user_id + features ML + label churned."""
    db = SessionLocal()
    try:
        sql = text("""
            SELECT
                user_id,
                session_count_7d,
                feature_breadth,
                avg_session_duration_min,
                days_since_last_use,
                engagement_score,
                churned,
                plan,
                segment
            FROM users
        """)
        result = db.execute(sql)
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=list(columns))
    finally:
        db.close()

    # Encodage plan
    df["plan_encoded"] = df["plan"].map({"free": 0, "pro": 1, "enterprise": 2}).fillna(0)
    df["churned"] = df["churned"].astype(int)

    return df
