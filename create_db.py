import sqlite3

conn = sqlite3.connect("shop.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER
)
""")

cursor.execute("""
INSERT INTO products (name, price)
VALUES
('น้ำสปอนเซอร์', 15),
('น้ำเปล่า', 10),
('มด', 300)
""")

conn.commit()

conn.close()

print("สร้างฐานข้อมูลสำเร็จ")