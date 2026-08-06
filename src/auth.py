from pathlib import Path
import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# ==========================================
# Database Path
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DB_PATH = DATABASE_DIR / "chat_history.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================
# Create Users Table
# ==========================================

def create_users_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# ==========================================
# Register User
# ==========================================

def register_user(username, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    try:

        cursor.execute("""
        INSERT INTO users(
            username,
            email,
            password
        )
        VALUES (?, ?, ?)
        """, (
            username,
            email,
            hashed_password
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# ==========================================
# Login User
# ==========================================

def login_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, password
    FROM users
    WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    conn.close()

    if user and check_password_hash(user[1], password):
        return user[0]

    return None