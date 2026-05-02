from sqlalchemy import text
from core.database import SessionLocal

def run_query(sql: str) -> list[dict]:
    """
    Execute a raw SQL query and return the results as a list of dicts.
    Falls back to empty list on error (keeps the pipeline alive during dev).
    """
    db = SessionLocal()
    try:
        result = db.execute(text(sql))
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]
    except Exception as e:
        print(f"[query_service] DB error: {e}")
        return []
    finally:
        db.close()
