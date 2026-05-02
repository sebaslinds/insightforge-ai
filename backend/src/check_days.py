
from core.database import SessionLocal
from core.models import User
import pandas as pd

db = SessionLocal()
try:
    users = db.query(User).all()
    if users:
        df = pd.DataFrame([{"days_since_last_use": u.days_since_last_use} for u in users])
        print("Average days_since_last_use:", df["days_since_last_use"].mean())
finally:
    db.close()
