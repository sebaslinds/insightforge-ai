import os
from sqlalchemy import text
from core.database import SessionLocal

db = SessionLocal()
try:
    sql = text("SELECT segment, COUNT(*), AVG(engagement_score), AVG(session_count_7d) FROM users GROUP BY segment;")
    res = db.execute(sql)
    print(f"{'Segment':<15} | {'Count':<6} | {'Avg Engag':<10} | {'Avg Sess7d':<10}")
    print("-" * 55)
    for row in res:
        print(f"{str(row[0]):<15} | {row[1]:<6} | {float(row[2]):<10.2f} | {float(row[3]):<10.2f}")
finally:
    db.close()
