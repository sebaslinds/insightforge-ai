
from core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    db.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction'"))
    db.commit()
    print("Sessions terminated")
finally:
    db.close()
