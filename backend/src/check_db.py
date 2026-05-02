
from core.database import SessionLocal
from core.models import User
import pandas as pd

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Total users: {len(users)}")
    if users:
        df = pd.DataFrame([{"engagement_score": u.engagement_score, "segment": u.segment} for u in users])
        print("Average engagement score:", df["engagement_score"].mean())
        print("Segments counts in DB:")
        print(df["segment"].value_counts())
finally:
    db.close()
