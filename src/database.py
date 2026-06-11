import sqlite3

def create_database():

    conn = sqlite3.connect("database/chat_history.db")
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


def save_chat(user_msg, bot_msg, sentiment):

    conn = sqlite3.connect("database/chat_history.db")
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


def get_all_chats():

    conn = sqlite3.connect("database/chat_history.db")
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


def get_chat_count():

    conn = sqlite3.connect("database/chat_history.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM chats
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


def get_sentiment_count(sentiment):

    conn = sqlite3.connect("database/chat_history.db")
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


def get_recent_chats():

    conn = sqlite3.connect("database/chat_history.db")
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