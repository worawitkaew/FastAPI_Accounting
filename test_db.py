import sqlite3

conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

# รันคำสั่ง SQL
cursor.execute("PRAGMA table_info(transactions);")

# ใช้ .fetchall() เพื่อดึงข้อมูลทั้งหมดออกมา
data = cursor.fetchall()

# แสดงผลลัพธ์
print(data)

conn.commit()
conn.close()