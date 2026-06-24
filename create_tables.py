import sqlite3

conn = sqlite3.connect("shop.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    image TEXT,
    cost_price REAL,
    sell_price REAL,
    stock INTEGER,
    owner TEXT,
    description TEXT
)
)
""")

conn.commit()

print("สร้าง transaction_items สำเร็จ")

conn.close()