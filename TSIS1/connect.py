# connect.py
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG


def get_connection():
    """Return a new psycopg2 connection using DB_CONFIG."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Apply schema.sql and procedures.sql to the database."""
    import os
    base = os.path.dirname(__file__)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for filename in ("schema.sql", "procedures.sql"):
                path = os.path.join(base, filename)
                with open(path, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
        conn.commit()
        print("Database initialised successfully.")
    finally:
        conn.close()
