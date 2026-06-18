import sqlite3

conn = sqlite3.connect("shop.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM products")

rows = cursor.fetchall()

print(rows)

conn.close()