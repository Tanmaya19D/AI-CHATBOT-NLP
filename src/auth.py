import sqlite3

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from src.database import get_connection


def create_users_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    hashed_password = generate_password_hash(
        password,
        method="scrypt"
    )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users(
                username,
                email,
                password
            )
            VALUES (?, ?, ?)
            """,
            (
                username,
                email,
                hashed_password
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:
        connection.rollback()

        return False

    finally:
        connection.close()


def login_user(username, password):
    username = username.strip()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            username,
            password
        FROM users
        WHERE LOWER(username) = LOWER(?)
        """,
        (username,)
    )

    user = cursor.fetchone()

    connection.close()

    if user is None:
        return None

    user_id = user[0]
    stored_password = user[2]

    if check_password_hash(
        stored_password,
        password
    ):
        return user_id

    return None