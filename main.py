from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

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
            "price": row[2]
        })

    return products