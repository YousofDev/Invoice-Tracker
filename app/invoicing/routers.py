from fastapi import APIRouter, Body, Depends
from typing import Annotated, List

from app.invoicing.service import InvoicingService
from app.invoicing.schemas import (
    ClientCreate,
    ClientUpdate,
    ClientInDB,
    ItemCreate,
    ItemUpdate,
    ItemInDB,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceInDB,
    PaymentCreate,
    PaymentUpdate,
    PaymentInDB,
)

router = APIRouter()

invoicing_service: InvoicingService = Depends()


@router.get("/clients", response_model=List[ClientInDB])
def get_client_list(invoicing_service, skip: int = 0, limit: int = 100):
    pass


@router.post("/clients", response_model=ClientInDB)
def create_client(invoicing_service, client: ClientCreate):
    pass


@router.get("/clients/{client_id}", response_model=ClientInDB)
def get_client(invoicing_service, client_id: int):
    pass


@router.put("/clients/{client_id}", response_model=ClientInDB)
def update_client(invoicing_service, client_id: int, client: ClientUpdate):
    pass


@router.delete("/clients/{client_id}")
def delete_client(invoicing_service, client_id: int):
    pass


@router.get("/items", response_model=List[ItemInDB])
def get_item_list(invoicing_service, skip: int = 0, limit: int = 100):
    pass


@router.post("/items", response_model=ItemInDB)
def create_item(invoicing_service, item: ItemCreate):
    pass


@router.get("/items/{item_id}", response_model=ItemInDB)
def get_item(invoicing_service, item_id: int):
    pass


@router.put("/items/{item_id}", response_model=ItemInDB)
def update_item(invoicing_service, item_id: int, item: ItemUpdate):
    pass


@router.delete("/items/{item_id}")
def delete_item(invoicing_service, item_id: int):
    pass


@router.get("/invoices")
def get_invoice_list(invoicing_service, skip: int = 0, limit: int = 100):
    return invoicing_service.get_invoice_list(skip, limit)


@router.post("/invoices", response_model=InvoiceInDB)
def create_invoice(invoicing_service, invoice: InvoiceCreate):
    return invoicing_service.create_invoice(invoice)


@router.get("/invoices/{invoice_id}", response_model=InvoiceInDB)
def get_invoice(invoicing_service, invoice_id: int):
    return invoicing_service.get_invoice(invoice_id)


@router.put("/invoices/{invoice_id}", response_model=InvoiceInDB)
def update_invoice(invoicing_service, invoice_id: int, invoice: InvoiceUpdate):
    return invoicing_service.update_invoice(invoice_id, invoice)


@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoicing_service, invoice_id: int):
    return invoicing_service.delete_invoice(invoice_id)


@router.get("/payments", response_model=List[PaymentInDB])
def get_payment_list(invoicing_service, skip: int = 0, limit: int = 100):
    pass


@router.post("/payments", response_model=PaymentInDB)
def create_payment(invoicing_service, payment: PaymentCreate):
    pass


@router.get("/payments/{payment_id}", response_model=PaymentInDB)
def get_payment(invoicing_service, payment_id: int):
    pass


@router.put("/payments/{payment_id}", response_model=PaymentInDB)
def update_payment(invoicing_service, payment_id: int, payment: PaymentUpdate):
    pass


@router.delete("/payments/{payment_id}")
def delete_payment(invoicing_service, payment_id: int):
    pass
