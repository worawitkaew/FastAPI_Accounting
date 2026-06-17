from fastapi import FastAPI,Request,Depends

from routes.api import api_router

from routes.utility.login import get_current_active_user
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event (runs before the app starts)
    print("App is starting")
    yield
    # Shutdown event (runs before the app shuts down)
    print("App is shutting down")

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/routes")

@app.get("/")
def root(current_user=Depends(get_current_active_user)):
    return {"message": "Hello World","current_user":current_user}

import time
@app.get("/test")
def root_test():
    time.sleep(2)
    return {"message_test": "Hello World_test"}


