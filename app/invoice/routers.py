from fastapi import APIRouter, Depends, status

from app.invoice.service import InvoiceService
from app.invoice.schemas import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceInDB,
)

router = APIRouter()

@router.get("/invoices")
def get_invoice_list(
    skip: int = 0, limit: int = 100, service: InvoiceService = Depends()
):
    return service.get_invoice_list(skip, limit)


@router.post("/invoices", status_code=status.HTTP_201_CREATED, response_model=InvoiceInDB)
def create_invoice(invoice: InvoiceCreate, service: InvoiceService = Depends()):
    return service.create_invoice(invoice)


@router.get("/invoices/{invoice_id}", response_model=InvoiceInDB)
def get_invoice(invoice_id: int, service: InvoiceService = Depends()):
    return service.get_invoice(invoice_id)


@router.put("/invoices/{invoice_id}", response_model=InvoiceInDB)
def update_invoice(
    invoice_id: int, invoice: InvoiceUpdate, service: InvoiceService = Depends()
):
    return service.update_invoice(invoice_id, invoice)


@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, service: InvoiceService = Depends()):
    return service.delete_invoice(invoice_id)
