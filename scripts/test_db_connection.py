# scripts/test_db_connection.py
from db.connection import get_connection

def main():
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            row = cur.fetchone()
            print("DB connected!")
            print("PostgreSQL version:", row["version"])

if __name__ == "__main__":
    main()