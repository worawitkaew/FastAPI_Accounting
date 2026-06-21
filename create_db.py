import sqlite3

conn = sqlite3.connect("shop.db")

cursor = conn.cursor()


conn.commit()

conn.close()

print("สร้างฐานข้อมูลสำเร็จ")