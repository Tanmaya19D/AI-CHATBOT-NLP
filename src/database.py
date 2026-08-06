import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "chat_history.db"


def get_connection():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        str(DATABASE_PATH),
        timeout=20
    )

    return connection


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chats(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def save_chat(user_msg, bot_msg, sentiment):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO chats(
            user_message,
            bot_response,
            sentiment
        )
        VALUES (?, ?, ?)
        """,
        (
            user_msg,
            bot_msg,
            sentiment
        )
    )

    connection.commit()
    connection.close()


def get_all_chats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            user_message,
            bot_response,
            sentiment,
            timestamp
        FROM chats
        ORDER BY id DESC
        """
    )

    chats = cursor.fetchall()

    connection.close()

    return chats


def get_chat_count():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM chats
        """
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count


def get_sentiment_count(sentiment):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM chats
        WHERE sentiment = ?
        """,
        (sentiment,)
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count


def get_recent_chats(limit=10):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            user_message,
            sentiment,
            timestamp
        FROM chats
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    chats = cursor.fetchall()

    connection.close()

    return chats