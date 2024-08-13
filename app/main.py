from fastapi import FastAPI

from app.auth.routers import router as auth_router
from app.invoicing.routers import router as invoice_router
from app.database import create_tables

create_tables()

app = FastAPI()

app.include_router(auth_router)
app.include_router(invoice_router)


@app.get("/")
def home():
    return {"response": "Invoice Tracker App"}
