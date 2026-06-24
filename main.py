from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel
from datetime import datetime

from fastapi import UploadFile
from fastapi import File
import shutil
import os

from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI()

######## แก้ 304 #############
from fastapi import Request

@app.middleware("http")
async def log_requests(
    request: Request,
    call_next
):

    response = await call_next(
        request
    )

    if request.url.path.startswith(
        "/uploads/"
    ):
        return response

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if response.status_code != 304:
        print(
            f"[{now}] "
            f"{request.method} "
            f"{request.url.path} "
            f"{response.status_code}"
        )
    if response.status_code >= 400:
        print(
            f"ERROR "
            f"{request.method} "
            f"{request.url.path} "
            f"{response.status_code}"
        )
    return response
######## แก้ 304 #############

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

class DepositRequest(
    BaseModel
):

    amount:int

    slip_image:str

    note:str=""

class CartItem(BaseModel):
    product_id: int
    quantity: int
class CheckoutRequest(BaseModel):
    items: list[CartItem]
    payment_method:str
    slip_image: str = ""

class LoginData(BaseModel):
    username: str
    password: str

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000"],
    allow_origins=["*"],
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
            "stock": row[5],
            "owner": row[6],
            "description": row[7],
            "category": row[8],
            "created_at": row[9],
            "update_at": row[10]
        })

    return products

#########################################################

class Product(BaseModel):
    name: str
    image: str | None = None

    cost_price: float
    sell_price: float
    stock: int
    owner: str
    description: str
    category: str
    # created_at:str
    # update_at:str

class Expense(BaseModel):
    description: str
    amount: int
    created_at: str

# เพิ่มสินค้า
@app.post("/products")
def create_product(product: Product):

    conn = sqlite3.connect("shop.db")
    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO products
        (
            name,
            image,
            cost_price,
            sell_price,
            stock,
            owner,
            description,
            category,
            created_at,
            update_at
        )
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product.name,
            product.image,
            product.cost_price,
            product.sell_price,
            product.stock,
            product.owner,
            product.description,
            product.category,
            now,
            now
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
@app.put(
    "/products/{product_id}"
)
def update_product(
    product_id: int,
    product: Product
):

    try:

        conn = sqlite3.connect(
            "shop.db"
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE products
            SET
              name=?,
              image=?,
              cost_price=?,
              sell_price=?,
              stock=?,
              owner=?,
              category=?,
              description=?,
              update_at=?
            WHERE id=?
            """,
            (
                product.name,
                product.image,
                product.cost_price,
                product.sell_price,
                product.stock,
                product.owner,
                product.category,
                product.description,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                product_id
            )
        )

        conn.commit()

        conn.close()

        return {
            "message":
            "แก้ไขสำเร็จ"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
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
            profit,
            payment_method,
            slip_image
        )
        VALUES (?, ?, ?, ? ,? ,?)
        """,
        (
            created_at,
            total_cost,
            total_sell,
            profit,
            data.payment_method,
            data.slip_image
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
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    cursor.execute(
        """
        SELECT
            COUNT(*) as total_bill,
            COALESCE(
                SUM(total_sell),
                0
            ) as total_sell,
            COALESCE(
                SUM(profit),
                0
            ) as total_profit
        FROM transactions
        WHERE DATE(created_at)=?
        """,
        (today,)
    )

    summary = dict(
        cursor.fetchone()
    )

    cursor.execute(
        """
        SELECT
            COALESCE(
                SUM(total_sell),
                0
            )
        FROM transactions
        WHERE payment_method='cash'
        AND DATE(created_at)=?
        """,
        (today,)
    )

    cash_today = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT
            COALESCE(
                SUM(total_sell),
                0
            )
        FROM transactions
        WHERE payment_method='transfer'
        AND DATE(created_at)=?
        """,
        (today,)
    )

    transfer_today = cursor.fetchone()[0]

    conn.close()

    return {

        "total_bill":
            summary["total_bill"],

        "total_sell":
            summary["total_sell"],

        "total_profit":
            summary["total_profit"],

        "cash_today":
            cash_today,

        "transfer_today":
            transfer_today

    }
@app.get("/transactions")
def get_transactions():

    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM transactions
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]

@app.get(
    "/transactions/{transaction_id}"
)
def get_transaction_detail(
    transaction_id: int
):

    conn = sqlite3.connect(
        "shop.db"
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            p.name,

            ti.quantity,

            ti.sell_price,

            (
                ti.quantity *
                ti.sell_price
            ) as total

        FROM
            transaction_items ti

        JOIN products p

        ON

            ti.product_id =
            p.id

        WHERE

            ti.transaction_id = ?

        """,
        (transaction_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [

        dict(row)

        for row in rows

    ]
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
@app.get("/owners")
def get_owners():

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM owners"
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in rows
    ]
@app.get("/categories")
def get_categories():

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM categories"
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in rows
    ]
@app.post("/upload-slip")
def upload_slip(
    file: UploadFile = File(...)
):

    os.makedirs(
        "uploads/slips",
        exist_ok=True
    )

    file_path = (
        f"uploads/slips/"
        f"{file.filename}"
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "filename":
        file.filename
    }
@app.get("/cash-pending")
def cash_pending():

    conn = sqlite3.connect(
        "shop.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
        COALESCE(
            SUM(total_sell),
            0
        )
        FROM transactions
        WHERE payment_method='cash'
        AND is_deposited=0
        """
    )

    total = cursor.fetchone()[0]

    conn.close()

    return {
        "pending_cash":
        total
    }

@app.post("/cash-deposit")
def cash_deposit(
    data: DepositRequest
):

    conn = sqlite3.connect(
        "shop.db"
    )

    cursor = conn.cursor()

    created_at = (
        datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    cursor.execute(
        """
        INSERT INTO
        cash_deposits
        (
            created_at,
            amount,
            slip_image,
            note
        )
        VALUES
        (?, ?, ?, ?)
        """,
        (
            created_at,
            data.amount,
            data.slip_image,
            data.note
        )
    )

    cursor.execute(
        """
        UPDATE transactions
        SET is_deposited=1
        WHERE payment_method='cash'
        AND is_deposited=0
        """
    )

    conn.commit()

    conn.close()

    return {
        "success":True
    }
@app.get("/cash-deposits")
def get_cash_deposits():

    conn = sqlite3.connect(
        "shop.db"
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM cash_deposits
        ORDER BY id DESC
        """
    )

    data = [

        dict(row)

        for row in

        cursor.fetchall()

    ]

    conn.close()

    return data

@app.get("/sales-chart")
def sales_chart():

    conn = sqlite3.connect(
        "shop.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

        DATE(created_at),

        SUM(total_sell)

        FROM transactions

        GROUP BY
        DATE(created_at)

        ORDER BY
        DATE(created_at)

        DESC

        LIMIT 7
        """
    )

    rows = cursor.fetchall()

    conn.close()

    rows.reverse()

    return [

        {
            "date": row[0],
            "total": row[1]
        }

        for row in rows

    ]