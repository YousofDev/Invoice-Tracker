from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.utils.logger import logger
from app.auth.routers import router as auth_router
from app.item.routers import router as item_router
from app.payment.routers import router as payment_router
from app.invoice.routers import router as invoice_router
from app.client.routers import router as client_router
from app.database import create_tables


app = FastAPI()

create_tables()

logger.basicConfig()
logger.getLogger("sqlalchemy.engine").setLevel(logger.INFO)


app.include_router(auth_router)
app.include_router(client_router)
app.include_router(item_router)
app.include_router(invoice_router)
app.include_router(payment_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"{exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"{exc._message}")
    return JSONResponse(
        status_code=500, content={"message": "A database error occurred."}
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={"message": "Validation error", "errors": exc.errors()},
    )


@app.get("/")
def home():
    return {"response": "Invoice Tracker App"}
