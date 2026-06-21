import sqlite3

conn = sqlite3.connect("shop.db")

cursor = conn.cursor()

cursor.execute(
    "SELECT id, username, role FROM users"
)

rows = cursor.fetchall()

print(rows)

conn.close()