from sqlalchemy import text
from core.database import engine

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE tenants ADD COLUMN total_carbon_footprint FLOAT DEFAULT 0.0'))
            conn.commit()
            print("Column total_carbon_footprint added.")
        except Exception as e:
            print(f"Migration error (might already exist): {e}")

if __name__ == "__main__":
    migrate()
