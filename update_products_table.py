import sqlite3

conn = sqlite3.connect("shop.db")

cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE products ADD COLUMN cost_price INTEGER DEFAULT 0"
    )
except:
    pass

try:
    cursor.execute(
        "ALTER TABLE products ADD COLUMN sell_price INTEGER DEFAULT 0"
    )
except:
    pass

try:
    cursor.execute(
        "ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 0"
    )
except:
    pass

conn.commit()

print("อัปเดต products table สำเร็จ")

conn.close()