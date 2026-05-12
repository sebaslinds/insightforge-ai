
from core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    sql = text("""
        SELECT pid, state, query, wait_event_type, wait_event 
        FROM pg_stat_activity 
        WHERE state != 'idle' AND query NOT LIKE '%pg_stat_activity%';
    """)
    res = db.execute(sql).fetchall()
    print("Active Queries & Locks:")
    for r in res:
        print(r)
finally:
    db.close()
