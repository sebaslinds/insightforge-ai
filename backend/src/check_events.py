
from core.database import SessionLocal
from sqlalchemy import text
import pandas as pd

db = SessionLocal()
try:
    sql = text("SELECT event_type, count(*) FROM events GROUP BY event_type")
    result = db.execute(sql).fetchall()
    print("Event counts by type:")
    for row in result:
        print(f"  {row[0]}: {row[1]}")
    
    sql_features = text("SELECT feature, count(*) FROM events WHERE event_type = 'feature_use' GROUP BY feature")
    result_features = db.execute(sql_features).fetchall()
    print("\nFeature use counts:")
    for row in result_features:
        print(f"  {row[0]}: {row[1]}")

finally:
    db.close()
