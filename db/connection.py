# db/connection.py
import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import settings


def get_connection():
    """
    PostgreSQL 커넥션을 하나 생성해서 반환.
    사용 후에는 conn.close() 되도록 with 문으로 감싸서 쓰는 걸 권장.
    """
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        cursor_factory=RealDictCursor,
    )
    return conn
