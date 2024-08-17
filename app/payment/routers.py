from fastapi import APIRouter, Depends
from typing import List

from app.payment.service import PaymentService
from app.payment.schemas import (
    PaymentCreate,
    PaymentUpdate,
    PaymentInDB,
)

router = APIRouter()


@router.get("/payments", response_model=List[PaymentInDB])
def get_payment_list(
    skip: int = 0, limit: int = 100, service: PaymentService = Depends()
):
    return service.get_payment_list(skip, limit)


@router.post("/payments", response_model=PaymentInDB)
def create_payment(payment: PaymentCreate, service: PaymentService = Depends()):
    return service.create_payment(payment)


@router.get("/payments/{payment_id}", response_model=PaymentInDB)
def get_payment(payment_id: int, service: PaymentService = Depends()):
    return service.get_payment(payment_id)


@router.put("/payments/{payment_id}", response_model=PaymentInDB)
def update_payment(
    payment_id: int, payment: PaymentUpdate, service: PaymentService = Depends()
):
    return service.update_payment(payment_id, payment)


@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, service: PaymentService = Depends()):
    return service.delete_payment(payment_id)
