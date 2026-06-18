from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    return [
        {
            "id": 1,
            "name": "น้ำสปอนเซอร์",
            "price": 15
        },
        {
            "id": 2,
            "name": "น้ำเปล่า",
            "price": 10
        },
        {
            "id": 3,
            "name": "มด",
            "price": 300
        }
    ]