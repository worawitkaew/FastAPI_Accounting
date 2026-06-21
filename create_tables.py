import sqlite3

conn = sqlite3.connect("shop.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    image TEXT,
    cost_price INTEGER,
    sell_price INTEGER,
    stock INTEGER
)
)
""")

conn.commit()

print("สร้าง transaction_items สำเร็จ")

conn.close()