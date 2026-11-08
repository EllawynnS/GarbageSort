import sqlite3
from pathlib import Path

db_file = Path(__file__).resolve().with_name("bin_identifier.db")

def init_database():
    connection = sqlite3.connect(db_file)
    try:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        confidence REAL,
        image BLOB,
        image_type TEXT
        )""")

        columns = {row[1] for row in cursor.execute("PRAGMA table_info(items)")}
        if "image" not in columns:
            cursor.execute("ALTER TABLE items ADD COLUMN image BLOB")

        connection.commit()
    finally:
        connection.close()

def save_item(category, confidence, image_bytes, image_type):
    conn = sqlite3.connect(db_file)
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO items (category, confidence, image, image_type) VALUES (?, ?, ?, ?)",
            (category, confidence, image_bytes, image_type),
        )
        conn.commit()
    finally:
        conn.close()

def get_latest_item():
    connection = sqlite3.connect(db_file)
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT category, confidence, image, image_type "
            "FROM items ORDER BY item_id DESC LIMIT 1"
        )
        return cursor.fetchone()
    finally:
        connection.close()