from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel
from datetime import datetime

from fastapi import UploadFile
from fastapi import File
import shutil
import os

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

class CartItem(BaseModel):
    product_id: int
    quantity: int
class CheckoutRequest(BaseModel):
    items: list[CartItem]
class LoginData(BaseModel):
    username: str
    password: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "ร้านดาวตก"
    }
@app.post("/upload")
def upload_image(file: UploadFile = File(...)):

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    file_path = f"uploads/{file.filename}"

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "filename": file.filename
    }
@app.get("/products")
def get_products():

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    rows = cursor.fetchall()

    conn.close()

    products = []

    for row in rows:

        products.append({
            "id": row[0],
            "name": row[1],
            "image": row[2],

            "cost_price": row[3],
            "sell_price": row[4],
            "stock": row[5]
        })

    return products

#########################################################

class Product(BaseModel):
    name: str
    image: str

    cost_price: float
    sell_price: float
    stock: int

class Expense(BaseModel):
    description: str
    amount: int
    created_at: str

# เพิ่มสินค้า
@app.post("/products")
def create_product(product: Product):

    conn = sqlite3.connect("shop.db")
    print(product)
    cursor = conn.cursor()

    cursor.execute(
    """
    INSERT INTO products
    (
        name,
        image,
        cost_price,
        sell_price,
        stock
    )
    VALUES (?, ?, ?, ?, ?)
    """,
        (
            product.name,
            product.image,
            product.cost_price,
            product.sell_price,
            product.stock
        )
    )

    conn.commit()

    conn.close()

    return {
        "message": "เพิ่มสินค้าสำเร็จ"
    }

# ลบสินคา
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT image
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    )

    row = cursor.fetchone()

    if row and row[0]:

        image_path = (
            "uploads/" + row[0]
        )

        if os.path.exists(image_path):

            os.remove(image_path)

    cursor.execute(
        """
        DELETE FROM products
        WHERE id = ?
        """,
        (product_id,)
    )

    conn.commit()

    conn.close()

    return {
        "message": "ลบสินค้าสำเร็จ"
    }
# 
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: Product
):

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE products
        SET
            name = ?,
            image = ?,
            cost_price = ?,
            sell_price = ?,
            stock = ?
        WHERE id = ?
        """,
        (
            product.name,
            product.image,
            product.cost_price,
            product.sell_price,
            product.stock,
            product_id
        )
    )

    conn.commit()

    conn.close()

    return {
        "message": "แก้ไขสินค้าสำเร็จ"
    }
@app.post("/login")
def login(data: LoginData):

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT username, role
        FROM users
        WHERE username = ?
        AND password = ?
        """,
        (
            data.username,
            data.password
        )
    )

    user = cursor.fetchone()

    conn.close()

    if user:

        return {
            "success": True,
            "username": user[0],
            "role": user[1]
        }

    return {
        "success": False,
        "message": "username หรือ password ไม่ถูกต้อง"
    }

@app.get("/expenses")
def get_expenses():

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses"
    )

    rows = cursor.fetchall()

    conn.close()

    expenses = []

    for row in rows:

        expenses.append({
            "id": row[0],
            "description": row[1],
            "amount": row[2],
            "created_at": row[3]
        })

    return expenses
@app.post("/expenses")
def create_expense(expense: Expense):

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO expenses
        (description, amount, created_at)
        VALUES (?, ?, ?)
        """,
        (
            expense.description,
            expense.amount,
            expense.created_at
        )
    )

    conn.commit()

    conn.close()

    return {
        "message": "เพิ่มรายจ่ายสำเร็จ"
    }

@app.get("/expenses/total")
def get_total_expense():

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT SUM(amount) FROM expenses"
    )

    total = cursor.fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    return {
        "total": total
    }

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()

    conn.close()

    return {
        "message": "ลบรายจ่ายสำเร็จ"
    }

@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    expense: Expense
):

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE expenses
        SET description = ?,
            amount = ?,
            created_at = ?
        WHERE id = ?
        """,
        (
            expense.description,
            expense.amount,
            expense.created_at,
            expense_id
        )
    )

    conn.commit()

    conn.close()

    return {
        "message": "แก้ไขรายจ่ายสำเร็จ"
    }

@app.post("/checkout")
def checkout(data: CheckoutRequest):

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    total_cost = 0
    total_sell = 0

    # ตรวจสอบสินค้าและคำนวณยอดรวม
    for item in data.items:

        cursor.execute(
            """
            SELECT
                cost_price,
                sell_price,
                stock
            FROM products
            WHERE id = ?
            """,
            (item.product_id,)
        )

        product = cursor.fetchone()

        if not product:

            conn.close()

            return {
                "success": False,
                "message": f"ไม่พบสินค้า id {item.product_id}"
            }

        cost_price = product[0]
        sell_price = product[1]
        stock = product[2]

        if item.quantity > stock:

            conn.close()

            return {
                "success": False,
                "message": f"สินค้า id {item.product_id} มีไม่พอในสต๊อก"
            }

        total_cost += cost_price * item.quantity
        total_sell += sell_price * item.quantity

    profit = total_sell - total_cost

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # สร้างหัวบิล
    cursor.execute(
        """
        INSERT INTO transactions
        (
            created_at,
            total_cost,
            total_sell,
            profit
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            created_at,
            total_cost,
            total_sell,
            profit
        )
    )

    transaction_id = cursor.lastrowid

    # บันทึกรายการสินค้าและตัดสต๊อก
    for item in data.items:

        cursor.execute(
            """
            SELECT
                cost_price,
                sell_price
            FROM products
            WHERE id = ?
            """,
            (item.product_id,)
        )

        product = cursor.fetchone()

        cost_price = product[0]
        sell_price = product[1]

        cursor.execute(
            """
            INSERT INTO transaction_items
            (
                transaction_id,
                product_id,
                quantity,
                cost_price,
                sell_price
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                transaction_id,
                item.product_id,
                item.quantity,
                cost_price,
                sell_price
            )
        )

        cursor.execute(
            """
            UPDATE products
            SET stock = stock - ?
            WHERE id = ?
            """,
            (
                item.quantity,
                item.product_id
            )
        )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "transaction_id": transaction_id,
        "total_cost": total_cost,
        "total_sell": total_sell,
        "profit": profit
    }

@app.get("/dashboard")
def dashboard():

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(total_sell), 0),
            COALESCE(SUM(total_cost), 0),
            COALESCE(SUM(profit), 0)
        FROM transactions
        """
    )

    row = cursor.fetchone()

    conn.close()

    return {
        "total_transactions": row[0],
        "total_sell": row[1],
        "total_cost": row[2],
        "total_profit": row[3]
    }

@app.get("/transactions")
def get_transactions():

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            created_at,
            total_cost,
            total_sell,
            profit
        FROM transactions
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    transactions = []

    for row in rows:

        transactions.append({
            "id": row[0],
            "created_at": row[1],
            "total_cost": row[2],
            "total_sell": row[3],
            "profit": row[4]
        })

    return transactions

@app.get("/transactions/{transaction_id}")
def get_transaction_detail(transaction_id: int):

    conn = sqlite3.connect("shop.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            transaction_items.id,
            transaction_items.product_id,
            products.name,
            transaction_items.quantity,
            transaction_items.cost_price,
            transaction_items.sell_price
        FROM transaction_items
        JOIN products
            ON products.id = transaction_items.product_id
        WHERE transaction_id = ?
        """,
        (transaction_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    items = []

    for row in rows:

        items.append({
            "id": row[0],
            "product_id": row[1],
            "name": row[2],
            "quantity": row[3],
            "cost_price": row[4],
            "sell_price": row[5]
        })

    return items

import os

@app.put("/products/{product_id}/image")
async def update_product_image(
    product_id: int,
    file: UploadFile = File(...)
):

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT image
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    )

    old_product = cursor.fetchone()

    if old_product and old_product[0]:

        old_image_path = (
            "uploads/" + old_product[0]
        )

        if os.path.exists(old_image_path):

            os.remove(old_image_path)

    file_path = (
        "uploads/" + file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        buffer.write(
            await file.read()
        )

    cursor.execute(
        """
        UPDATE products
        SET image = ?
        WHERE id = ?
        """,
        (
            file.filename,
            product_id
        )
    )

    conn.commit()

    conn.close()

    return {
        "message": "เปลี่ยนรูปสำเร็จ",
        "filename": file.filename
    }