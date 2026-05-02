import psycopg2
from psycopg2.extras import DictCursor
import datetime

DB_CONFIG = {
    "dbname": "snake_game",
    "user": "aigera8111icloud.com",      # change as needed
    "password": "",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_or_create_player(username):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    player = cur.fetchone()
    if not player:
        cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
        player_id = cur.fetchone()['id']
        conn.commit()
    else:
        player_id = player['id']
    cur.close()
    conn.close()
    return player_id

def save_game_result(username, score, level):
    player_id = get_or_create_player(username)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO game_sessions (player_id, score, level_reached)
        VALUES (%s, %s, %s)
    """, (player_id, score, level))
    conn.commit()
    cur.close()
    conn.close()

def get_top_10():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("""
        SELECT p.username, g.score, g.level_reached, g.played_at
        FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        ORDER BY g.score DESC, g.played_at DESC
        LIMIT 10
    """)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def get_personal_best(username):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("""
        SELECT MAX(g.score) as best_score, MAX(g.level_reached) as best_level
        FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        WHERE p.username = %s
    """, (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result['best_score'] if result and result['best_score'] else 0