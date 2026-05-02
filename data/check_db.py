
import os
import pg8000
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS").strip('"')
DB_NAME = os.getenv("DB_NAME")

def main():
    try:
        conn = pg8000.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host='localhost', port=5432)
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
