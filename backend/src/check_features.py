
from core.database import SessionLocal
from sqlalchemy import text
import pandas as pd

db = SessionLocal()
try:
    sql = text("SELECT session_count_7d, feature_breadth, avg_session_duration_min, days_since_last_use, engagement_score FROM users")
    df = pd.read_sql(sql, db.bind)
    print("Features Statistics:")
    print(df.describe())
finally:
    db.close()
