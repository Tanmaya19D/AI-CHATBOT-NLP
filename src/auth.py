import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

DB_NAME = "chatbot.db"


def register_user(username, email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute("""
            INSERT INTO users
            (username, email, password)
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


def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
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