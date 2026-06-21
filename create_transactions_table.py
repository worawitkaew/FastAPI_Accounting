import sqlite3

conn = sqlite3.connect("shop.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    total_cost INTEGER,
    total_sell INTEGER,
    profit INTEGER
)
""")

conn.commit()

print("สร้าง transactions สำเร็จ")

conn.close()