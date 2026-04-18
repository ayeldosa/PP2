import psycopg2
from config import config

def get_connection():
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        print("Connection error:", e)