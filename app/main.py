from fastapi import FastAPI
from app.auth.routers import router as auth_router
from app.invoice.routers import router as invoice_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(invoice_router)


@app.get("/")
def home():
    return {"message": "Invoice Tracker App"}
