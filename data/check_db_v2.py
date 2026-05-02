
import os
import pg8000
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector

load_dotenv()
os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS").strip('"') if os.getenv("DB_PASS") else ""
DB_NAME = os.getenv("DB_NAME")
INSTANCE_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")

def get_conn():
    connector = Connector()
    return connector.connect(
        INSTANCE_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )

def main():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM events")
        events_count = cursor.fetchone()[0]
        print(f"Users: {users_count}")
        print(f"Events: {events_count}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
