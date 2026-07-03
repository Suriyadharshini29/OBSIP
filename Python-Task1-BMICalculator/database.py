import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "bmi_data.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    try:
        with get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                )
            """)
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Database init failed: {e}")


def save_record(username: str, weight: float, height: float, bmi: float, category: str):
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO bmi_records (username, weight, height, bmi, category, recorded_at) VALUES (?, ?, ?, ?, ?, ?)",
                (username.strip(), weight, height, bmi, category, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to save record: {e}")


def get_records(username: str):
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT recorded_at, bmi, category, weight, height FROM bmi_records WHERE username = ? ORDER BY recorded_at ASC",
                (username.strip(),)
            )
            return cursor.fetchall()
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to fetch records: {e}")


def get_all_users():
    try:
        with get_connection() as conn:
            cursor = conn.execute("SELECT DISTINCT username FROM bmi_records ORDER BY username ASC")
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to fetch users: {e}")


def delete_user_records(username: str):
    try:
        with get_connection() as conn:
            conn.execute("DELETE FROM bmi_records WHERE username = ?", (username.strip(),))
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to delete records: {e}")
