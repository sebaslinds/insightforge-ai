from core.database import SessionLocal
from core.models import User, Event, BusinessRule, Notification
from core.tenant_models import Tenant, AdminUser
import random

def update_cac():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"Updating {len(users)} users...")
    
    channels = {
        "google_ads": (80, 150),
        "linkedin": (120, 250),
        "organic": (0, 0),
        "referral": (10, 40),
        "twitter": (40, 90)
    }
    channel_list = list(channels.keys())
    weights = [0.3, 0.2, 0.35, 0.1, 0.05]

    for u in users:
        channel = random.choices(channel_list, weights=weights)[0]
        cost_min, cost_max = channels[channel]
        u.acquisition_channel = channel
        u.acquisition_cost = random.uniform(cost_min, cost_max)
    
    db.commit()
    db.close()
    print("Done.")

if __name__ == "__main__":
    update_cac()
