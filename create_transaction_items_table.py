import sqlite3

conn = sqlite3.connect("shop.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transaction_items (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    transaction_id INTEGER,

    product_id INTEGER,

    quantity INTEGER,

    cost_price INTEGER,

    sell_price INTEGER

)
""")

conn.commit()

print("สร้าง transaction_items สำเร็จ")

conn.close()