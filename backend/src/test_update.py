
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))
from core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("Testing UPDATE...")
    res = db.execute(text("UPDATE users SET segment = 'test_segment' WHERE segment IS NULL LIMIT 10"))
    db.commit()
    print(f"Updated {res.rowcount} rows.")
finally:
    db.close()
