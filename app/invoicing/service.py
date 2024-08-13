from decimal import Decimal
from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime

from app.database import get_db
from app.auth.models import User
from app.invoicing.models import Client, Item, Invoice, InvoiceItem, Payment
from app.invoicing.schemas import (
    ClientCreate,
    ClientUpdate,
    ClientInDB,
    InvoiceItemInDB,
    ItemCreate,
    ItemUpdate,
    ItemInDB,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceInDB,
    PaymentCreate,
    PaymentUpdate,
    PaymentInDB,
    InvoiceStatus,
    PaymentStatus,
    PaymentMethod,
)


class InvoicingService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # Client Operations:
    def get_client_list(self, skip: int = 0, limit: int = 100):
        clients = self.db.query(Client).offset(skip).limit(limit).all()
        return clients

    def get_client(self, client_id: int) -> ClientInDB:
        client = self.find_client(client_id)
        return ClientInDB.model_validate(client)

    def create_client(self, client_data: ClientCreate) -> ClientInDB:
        client_dict = client_data.model_dump()

        client = Client(**client_dict)
        self.db.add(client)

        self.db.commit()
        self.db.refresh(client)

        return ClientInDB.model_validate(client)

    def update_client(self, client_id: int, client_data: ClientUpdate) -> ClientInDB:
        client_dict = client_data.model_dump()

        stmt = (
            update(Client)
            .where(Client.id == client_id)
            .values(**client_dict)
            .returning(Client)
        )

        result = self.db.execute(stmt)
        updated_client = result.scalar_one()

        self.db.commit()

        return ClientInDB.model_validate(updated_client)

    def delete_client(self, client_id: int) -> None:
        stmt = delete(Client).where(Client.id == client_id)
        self.db.execute(stmt)
        self.db.commit()

    # Item Operations:
    def get_item_list(self, skip: int = 0, limit: int = 100):
        clients = self.db.query(Item).offset(skip).limit(limit).all()
        return clients

    def get_item(self, item_id: int) -> ItemInDB:
        item = self.find_item(item_id)
        return ItemInDB.model_validate(item)

    def create_item(self, item_data: ItemCreate) -> ItemInDB:
        item_dict = item_data.model_dump()

        item = Item(**item_dict)
        self.db.add(item)

        self.db.commit()
        self.db.refresh(item)

        return ItemInDB.model_validate(item)

    def update_item(self, item_id: int, item_data: ItemUpdate) -> ItemInDB:
        item_dict = item_data.model_dump()

        stmt = (
            update(Item).where(Item.id == item_id).values(**item_dict).returning(Item)
        )

        result = self.db.execute(stmt)
        updated_item = result.scalar_one()

        self.db.commit()

        return ItemInDB.model_validate(updated_item)

    def delete_item(self, item_id: int) -> None:
        stmt = delete(Item).where(Item.id == item_id)
        self.db.execute(stmt)
        self.db.commit()

    # Invoice Operations:
    def get_invoice_list(self, skip: int = 0, limit: int = 100):
        invoices = self.db.query(Invoice).offset(skip).limit(limit).all()
        return invoices

    def get_invoice(self, invoice_id: int) -> InvoiceInDB:
        invoice = self.find_invoice(invoice_id)
        invoice_items = self.find_invoice_items(invoice_id)
        invoice_items_pydantic = [
            InvoiceItemInDB.model_validate(item) for item in invoice_items
        ]
        invoice_pydantic = InvoiceInDB.model_validate(invoice)
        invoice_pydantic.items = invoice_items_pydantic

        return invoice_pydantic

    def create_invoice(self, invoice_data: InvoiceCreate) -> InvoiceInDB:
        invoice_dict = invoice_data.model_dump()
        items = invoice_dict.pop("items")

        # Create the invoice
        invoice_stmt = insert(Invoice).values(**invoice_dict).returning(Invoice)
        result = self.db.execute(invoice_stmt)
        invoice = result.scalar_one()

        # Prepare invoice items data
        invoice_items_data = []
        for item in items:
            item_dict = item.model_dump()
            item_dict["invoice_id"] = invoice.id
            item_dict["item_amount"] = Decimal(str(item_dict["quantity"])) * Decimal(
                str(item_dict["price"])
            )
            invoice_items_data.append(item_dict)

        # Bulk insert invoice items
        invoice_items_stmt = (
            insert(InvoiceItem).values(invoice_items_data).returning(InvoiceItem)
        )
        result = self.db.execute(invoice_items_stmt)
        invoice_items = result.scalars().all()

        # Recalculate and update the total amount
        total_amount = sum(item["item_amount"] for item in invoice_items_data)
        self.db.execute(
            update(Invoice)
            .where(Invoice.id == invoice.id)
            .values(total_amount=total_amount)
        )

        # Refresh the invoice to get the updated total_amount
        self.db.refresh(invoice)

        # Commit the transaction
        self.db.commit()

        # Convert to Pydantic models
        invoice_items_pydantic = [
            InvoiceItemInDB.model_validate(item) for item in invoice_items
        ]
        invoice_pydantic = InvoiceInDB.model_validate(invoice)
        invoice_pydantic.items = invoice_items_pydantic

        return invoice_pydantic

    def update_invoice(
        self, invoice_id: int, invoice_data: InvoiceUpdate
    ) -> InvoiceInDB:
        invoice_dict = invoice_data.model_dump(exclude_unset=True)
        items = invoice_dict.pop("items", None)

        # Update the invoice
        self.db.execute(
            update(Invoice).where(Invoice.id == invoice_id).values(**invoice_dict)
        )

        if items is not None:
            # Delete existing items
            self.db.execute(
                delete(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id)
            )

            # Prepare new invoice items data
            invoice_items_data = []
            for item in items:
                item_dict = item.model_dump()
                item_dict["invoice_id"] = invoice_id
                item_dict["item_amount"] = Decimal(
                    str(item_dict["quantity"])
                ) * Decimal(str(item_dict["price"]))
                invoice_items_data.append(item_dict)

            # Bulk insert new invoice items
            invoice_items_stmt = (
                insert(InvoiceItem).values(invoice_items_data).returning(InvoiceItem)
            )
            result = self.db.execute(invoice_items_stmt)
            invoice_items = result.scalars().all()

            # Recalculate and update the total amount
            total_amount = sum(item["item_amount"] for item in invoice_items_data)
            self.db.execute(
                update(Invoice)
                .where(Invoice.id == invoice_id)
                .values(total_amount=total_amount)
            )

        # Fetch the updated invoice
        stmt = select(Invoice).where(Invoice.id == invoice_id)
        result = self.db.execute(stmt)
        invoice = result.scalar_one()

        # Fetch the updated invoice items
        stmt = select(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id)
        result = self.db.execute(stmt)
        invoice_items = result.scalars().all()

        # Commit the transaction
        self.db.commit()

        # Convert to Pydantic models
        invoice_items_pydantic = [
            InvoiceItemInDB.model_validate(item) for item in invoice_items
        ]
        invoice_pydantic = InvoiceInDB.model_validate(invoice)
        invoice_pydantic.items = invoice_items_pydantic

        return invoice_pydantic

    def delete_invoice(self, invoice_id: int) -> None:
        stmt = delete(Invoice).where(Invoice.id == invoice_id)
        self.db.execute(stmt)
        self.db.commit()

    # Payment Operations:
    def get_payment_list(self, skip: int = 0, limit: int = 100):
        payments = self.db.query(Payment).offset(skip).limit(limit).all()
        return payments

    def get_payment(self, payment_id: int) -> PaymentInDB:
        payment = self.find_payment(payment_id)
        return PaymentInDB.model_validate(payment)

    def create_payment(self, payment_data: PaymentCreate) -> PaymentInDB:
        payment_dict = payment_data.model_dump()

        payment = Payment(**payment_dict)
        self.db.add(payment)

        self.db.commit()
        self.db.refresh(payment)

        return PaymentInDB.model_validate(payment)

    def update_payment(
        self, payment_id: int, payment_data: PaymentUpdate
    ) -> PaymentInDB:
        payment_dict = payment_data.model_dump()

        stmt = (
            update(Payment)
            .where(Payment.id == payment_id)
            .values(**payment_dict)
            .returning(Payment)
        )

        result = self.db.execute(stmt)
        updated_payment = result.scalar_one()

        self.db.commit()

        return PaymentInDB.model_validate(updated_payment)

    def delete_payment(self, payment_id: int) -> None:
        stmt = delete(Payment).where(Payment.id == payment_id)
        self.db.execute(stmt)
        self.db.commit()

    def find_client(self, id: int) -> Client:
        resource = self.db.query(Client).filter(Client.id == id).first()
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )
        return resource

    def find_item(self, id: int) -> Item:
        resource = self.db.query(Item).filter(Item.id == id).first()
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )
        return resource

    def find_invoice(self, id: int) -> Invoice:
        resource = self.db.query(Invoice).filter(Invoice.id == id).first()
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
            )
        return resource

    def find_invoice_items(self, id: int) -> list[InvoiceItem]:
        return self.db.query(InvoiceItem).filter(Invoice.id == id).all()

    def find_payment(self, id: int) -> Payment:
        resource = self.db.query(Payment).filter(Payment.id == id).first()
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
            )
        return resource
