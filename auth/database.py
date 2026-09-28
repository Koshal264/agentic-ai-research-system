import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "users.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    # Chat sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        )
    """)

    conn.commit()
    conn.close()


def create_user(
    username: str,
    password_hash: str,
    role: str = "user"
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, role)
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_user(username: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, password_hash, role
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    return {
        "id": user[0],
        "username": user[1],
        "password_hash": user[2],
        "role": user[3]
    }


# -----------------------------
# CHAT HISTORY FUNCTIONS
# -----------------------------

def create_chat(user_id: int, title: str = "New Chat"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chats (user_id, title)
        VALUES (?, ?)
        """,
        (user_id, title)
    )

    chat_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return chat_id


def get_user_chats(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, created_at, updated_at
        FROM chats
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,)
    )

    chats = cursor.fetchall()

    conn.close()

    return [
        {
            "id": chat[0],
            "title": chat[1],
            "created_at": chat[2],
            "updated_at": chat[3]
        }
        for chat in chats
    ]


def get_chat(chat_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, created_at, updated_at
        FROM chats
        WHERE id = ? AND user_id = ?
        """,
        (chat_id, user_id)
    )

    chat = cursor.fetchone()

    conn.close()

    if not chat:
        return None

    return {
        "id": chat[0],
        "title": chat[1],
        "created_at": chat[2],
        "updated_at": chat[3]
    }


def add_message(
    chat_id: int,
    role: str,
    content: str
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages (chat_id, role, content)
        VALUES (?, ?, ?)
        """,
        (chat_id, role, content)
    )

    cursor.execute(
        """
        UPDATE chats
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (chat_id,)
    )

    conn.commit()
    conn.close()


def get_chat_messages(chat_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    # First verify ownership
    cursor.execute(
        """
        SELECT id
        FROM chats
        WHERE id = ? AND user_id = ?
        """,
        (chat_id, user_id)
    )

    chat = cursor.fetchone()

    if not chat:
        conn.close()
        return None

    cursor.execute(
        """
        SELECT id, role, content, created_at
        FROM messages
        WHERE chat_id = ?
        ORDER BY id ASC
        """,
        (chat_id,)
    )

    messages = cursor.fetchall()

    conn.close()

    return [
        {
            "id": message[0],
            "role": message[1],
            "content": message[2],
            "created_at": message[3]
        }
        for message in messages
    ]


def delete_chat(chat_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    # Verify ownership
    cursor.execute(
        """
        SELECT id
        FROM chats
        WHERE id = ? AND user_id = ?
        """,
        (chat_id, user_id)
    )

    chat = cursor.fetchone()

    if not chat:
        conn.close()
        return False

    # Delete messages first
    cursor.execute(
        """
        DELETE FROM messages
        WHERE chat_id = ?
        """,
        (chat_id,)
    )

    # Delete chat
    cursor.execute(
        """
        DELETE FROM chats
        WHERE id = ? AND user_id = ?
        """,
        (chat_id, user_id)
    )

    conn.commit()
    conn.close()

    return True