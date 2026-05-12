from core.database import SessionLocal
from core.models import User
import pandas as pd

db = SessionLocal()
users = db.query(User).limit(10).all()
for u in users:
    print(f"User {u.user_id}: CAC={u.acquisition_cost}, Channel={u.acquisition_channel}")
db.close()
