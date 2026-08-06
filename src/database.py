import sqlite3
from pathlib import Path

# ==========================
# Database Path
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "chat_history.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


# ==========================
# Create Database
# ==========================

def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        bot_response TEXT,
        sentiment TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# ==========================
# Save Chat
# ==========================

def save_chat(user_msg, bot_msg, sentiment):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chats(
            user_message,
            bot_response,
            sentiment
        )
        VALUES (?, ?, ?)
        """,
        (user_msg, bot_msg, sentiment)
    )

    conn.commit()
    conn.close()


# ==========================
# Get All Chats
# ==========================

def get_all_chats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        user_message,
        bot_response,
        sentiment,
        timestamp
    FROM chats
    ORDER BY id DESC
    """)

    chats = cursor.fetchall()

    conn.close()

    return chats


# ==========================
# Chat Count
# ==========================

def get_chat_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM chats
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


# ==========================
# Sentiment Count
# ==========================

def get_sentiment_count(sentiment):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM chats
        WHERE sentiment = ?
        """,
        (sentiment,)
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


# ==========================
# Recent Chats
# ==========================

def get_recent_chats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        user_message,
        sentiment,
        timestamp
    FROM chats
    ORDER BY id DESC
    LIMIT 10
    """)

    chats = cursor.fetchall()

    conn.close()

    return chats