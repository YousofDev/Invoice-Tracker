from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, insert, update
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.payment.models import Payment
from app.invoice.models import Invoice, InvoiceItem
from app.invoice.schemas import (
    InvoiceItemInDB,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceInDB,
)



class InvoiceService:

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_invoice_list(self, skip: int = 0, limit: int = 100) -> List[InvoiceInDB]:

        if limit > 100:
            limit = 100

        invoices = (
            self.db.query(Invoice)
            .join(Invoice.invoice_items)
            .join(InvoiceItem.item)
            .options(joinedload(Invoice.invoice_items).joinedload(InvoiceItem.item))
            .offset(skip)
            .limit(limit)
            .all()
        )

        if not invoices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No invoices found"
            )

        invoice_list = []
        for invoice in invoices:
            invoice_items = [
                InvoiceItemInDB(**item.__dict__, item_name=item.item.name)
                for item in invoice.invoice_items
            ]

            invoice_in_db = InvoiceInDB(**invoice.__dict__, items=invoice_items)
            invoice_list.append(invoice_in_db)

        return invoice_list

    def get_invoice(self, invoice_id: int) -> InvoiceInDB:
        invoice = (
            self.db.query(Invoice)
            .join(Invoice.invoice_items)
            .join(InvoiceItem.item)
            .options(joinedload(Invoice.invoice_items).joinedload(InvoiceItem.item))
            .filter(Invoice.id == invoice_id)
            .first()
        )

        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
            )

        invoice_items = [
            InvoiceItemInDB(**item.__dict__, item_name=item.item.name)
            for item in invoice.invoice_items
        ]

        return InvoiceInDB(**invoice.__dict__, items=invoice_items)

    def create_invoice(self, invoice_data: InvoiceCreate) -> InvoiceInDB:
        invoice_dict = invoice_data.model_dump()
        items = invoice_dict.pop("items")

        try:
            with self.db.begin():
                invoice_stmt = insert(Invoice).values(**invoice_dict).returning(Invoice)
                result = self.db.execute(invoice_stmt)
                invoice = result.scalar_one()

                invoice_items_data = []
                for item in items:
                    item_dict = item
                    item_dict["invoice_id"] = invoice.id
                    invoice_items_data.append(item_dict)

                invoice_items_stmt = (
                    insert(InvoiceItem)
                    .values(invoice_items_data)
                    .returning(InvoiceItem)
                )

                result = self.db.execute(invoice_items_stmt)

                invoice_items = result.scalars().all()

                total_amount = sum(item["quantity"] * item["price"] for item in items)

                # Update the invoice
                invoice_stmt = (
                    update(Invoice)
                    .where(Invoice.id == invoice.id)
                    .values(total_amount=total_amount)
                    .returning(Invoice)
                )

                result = self.db.execute(invoice_stmt)
                invoice = result.scalar_one()

                invoice_items_pydantic = [
                    InvoiceItemInDB(**item.__dict__, item_name=item.item.name)
                    for item in invoice_items
                ]

                return InvoiceInDB(
                    **invoice.__dict__,
                    items=invoice_items_pydantic,
                )

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(e),
            )

    def update_invoice(
        self, invoice_id: int, invoice_data: InvoiceUpdate
    ) -> InvoiceInDB:

        # Check if there is related payments:
        payment = (
            self.db.query(Payment).filter(Payment.invoice_id == invoice_id).first()
        )
        if payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice can not be updated if there is a related payments",
            )

        invoice_dict = invoice_data.model_dump()
        items = invoice_dict.pop("items")

        # Update the invoice
        invoice_stmt = (
            update(Invoice)
            .where(Invoice.id == invoice_id)
            .values(**invoice_dict)
            .returning(Invoice)
        )
        result = self.db.execute(invoice_stmt)
        invoice = result.scalar_one()

        # Delete existing items
        self.db.execute(delete(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id))

        invoice_items_data = []
        for item in items:
            item_dict = item
            item_dict["invoice_id"] = invoice.id
            invoice_items_data.append(item_dict)

        invoice_items_stmt = (
            insert(InvoiceItem).values(invoice_items_data).returning(InvoiceItem)
        )

        result = self.db.execute(invoice_items_stmt)

        invoice_items = result.scalars().all()

        total_amount = sum(item["quantity"] * item["price"] for item in items)

        # Update the invoice
        invoice_stmt = (
            update(Invoice)
            .where(Invoice.id == invoice.id)
            .values(total_amount=total_amount)
            .returning(Invoice)
        )

        result = self.db.execute(invoice_stmt)
        invoice = result.scalar_one()

        invoice_items_pydantic = [
            InvoiceItemInDB(**item.__dict__, item_name=item.item.name)
            for item in invoice_items
        ]

        return InvoiceInDB(
            **invoice.__dict__,
            items=invoice_items_pydantic,
        )

    def delete_invoice(self, invoice_id: int) -> None:
        stmt = delete(Invoice).where(Invoice.id == invoice_id)
        self.db.execute(stmt)
        self.db.commit()
