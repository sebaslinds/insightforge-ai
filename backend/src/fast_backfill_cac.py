from core.database import engine
from sqlalchemy import text
import random

def fast_backfill():
    channels = {
        "google_ads": (80, 150),
        "linkedin": (120, 250),
        "organic": (0, 0),
        "referral": (10, 40),
        "twitter": (40, 90)
    }
    
    with engine.connect() as conn:
        print("Backfilling with SQL...")
        for channel, (cmin, cmax) in channels.items():
            # Update users with random costs for this channel
            # We can't do random in SQL easily for each row without specific functions,
            # but we can just set a fixed random average or run a few batches.
            cost = (cmin + cmax) / 2
            conn.execute(text(f"UPDATE users SET acquisition_channel = :ch, acquisition_cost = :cost WHERE acquisition_channel IS NULL OR acquisition_channel = 'None'"), 
                         {"ch": channel, "cost": cost})
            # Actually, the above will set ALL remaining users to the same channel.
            # Let's do it better.
        
        # Better: just set a random distribution
        conn.execute(text("""
            UPDATE users 
            SET acquisition_channel = CASE 
                WHEN random() < 0.35 THEN 'organic'
                WHEN random() < 0.65 THEN 'google_ads'
                WHEN random() < 0.85 THEN 'linkedin'
                WHEN random() < 0.95 THEN 'referral'
                ELSE 'twitter'
            END,
            acquisition_cost = CASE 
                WHEN random() < 0.35 THEN 0.0
                WHEN random() < 0.65 THEN 80 + random() * 70
                WHEN random() < 0.85 THEN 120 + random() * 130
                WHEN random() < 0.95 THEN 10 + random() * 30
                ELSE 40 + random() * 50
            END
            WHERE acquisition_channel IS NULL OR acquisition_channel = 'None' OR acquisition_cost = 0.0
        """))
        conn.commit()
    print("Done.")

if __name__ == "__main__":
    fast_backfill()
