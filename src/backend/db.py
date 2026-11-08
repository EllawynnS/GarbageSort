import sqlite3

#We should be creating the database here 

db_file = "bin_identifier.db"

def init_database():
    connection = sqlite3.connect(db_file)

    cursor = connection.cursor()


    cursor.execute("""CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    confidence REAL,
    image_type TEXT
    )""")

    #closing the database

    connection.commit()
    connection.close()

def save_item(category, confidence, image_bytes, image_type):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute(
        "INSERT INTO items (category, confidence, image, image_type) VALUES (?, ?, ?, ?)",
        (category, confidence, image_bytes, image_type),
    )

    conn.commit()
    conn.close()

def get_latest_item():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute("SELECT category, confidence, image, image_type FROM items ORDER BY item_id DESC LIMIT 1")
    row = cursor.fetchone()

    connection.close()
    return row