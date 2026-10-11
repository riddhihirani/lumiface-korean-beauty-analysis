import sqlite3
import os
from typing import Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.getenv("DATABASE_PATH", os.path.join(DB_DIR, "lumiface.db"))

def init_db():
    """Initialize SQLite database schema for persistent user accounts."""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    # Seed demo account if database is freshly created and empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        from app.core.security import hash_password
        cursor.execute(
            "INSERT INTO users (email, full_name, password_hash) VALUES (?, ?, ?)",
            ("demo@lumiface.ai", "Demo Guest", hash_password("LumiFace2026!"))
        )
        conn.commit()

    conn.close()

def get_db_connection():
    """Return SQLite database connection with row factory."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
