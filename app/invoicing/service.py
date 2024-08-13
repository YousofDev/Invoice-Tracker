from fastapi import Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.auth.models import User
from app.invoicing.schemas import InvoiceStatus, PaymentStatus, PaymentMethod
from app.invoicing.models import Client, Item, Invoice, InvoiceItem, Payment


class InvoicingService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # Client Operations
    def create_client(
        self,
        owner_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Client:
        new_client = Client(
            owner_id=owner_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            phone=phone,
        )
        self.db.add(new_client)
        self.db.commit()
        self.db.refresh(new_client)
        return new_client

    def get_client(self, client_id: int) -> Client:
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )
        return client

    def update_client(self, client_id: int, **kwargs) -> Client:
        client = self.get_client(client_id)
        for key, value in kwargs.items():
            if hasattr(client, key):
                setattr(client, key, value)
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete_client(self, client_id: int) -> None:
        client = self.get_client(client_id)
        self.db.delete(client)
        self.db.commit()

    # Item Operations
    def create_item(
        self, owner_id: int, name: str, price: float, description: Optional[str] = None
    ) -> Item:
        new_item = Item(
            owner_id=owner_id, name=name, description=description, price=price
        )
        self.db.add(new_item)
        self.db.commit()
        self.db.refresh(new_item)
        return new_item

    def get_item(self, item_id: int) -> Item:
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )
        return item

    def update_item(self, item_id: int, **kwargs) -> Item:
        item = self.get_item(item_id)
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item_id: int) -> None:
        item = self.get_item(item_id)
        self.db.delete(item)
        self.db.commit()

    # Invoice Operations
    def create_invoice(
        self,
        owner_id: int,
        client_id: int,
        issuing_date: datetime,
        due_date: datetime,
        invoice_items: List[dict],
    ) -> Invoice:
        total_amount = 0
        invoice = Invoice(
            owner_id=owner_id,
            client_id=client_id,
            issuing_date=issuing_date,
            due_date=due_date,
            status=InvoiceStatus.DRAFT,
            total_amount=total_amount,
        )
        self.db.add(invoice)
        self.db.flush()  # To get the invoice id for creating invoice items

        for item_data in invoice_items:
            item = self.get_item(item_data["item_id"])
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                item_id=item.id,
                quantity=item_data["quantity"],
                price=item.price,
                item_amount=item.price * item_data["quantity"],
            )
            total_amount += invoice_item.item_amount
            self.db.add(invoice_item)

        # Update invoice total amount
        self.db.query(Invoice).filter(Invoice.id == invoice.id).update(
            {"total_amount": total_amount}
        )
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
            )
        return invoice

    def update_invoice(self, invoice_id: int, **kwargs) -> Invoice:
        invoice = self.get_invoice(invoice_id)
        for key, value in kwargs.items():
            if hasattr(invoice, key):
                setattr(invoice, key, value)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def delete_invoice(self, invoice_id: int) -> None:
        invoice = self.get_invoice(invoice_id)
        self.db.delete(invoice)
        self.db.commit()

    def add_payment_to_invoice(self, invoice_id: int, payment_amount: float) -> Invoice:
        # Fetch the invoice
        invoice = self.get_invoice(invoice_id)

        # Ensure invoice exists
        if invoice is None:
            raise ValueError("Invoice not found")

        # Calculate the new paid amount
        new_paid_amount = invoice["paid_amount"] + payment_amount

        # Determine the new status and fully paid date based on the new paid amount
        if new_paid_amount >= invoice.total_amount:
            status = InvoiceStatus.PAID
            fully_paid_date = datetime.now()
            paid_amount = invoice.total_amount
        elif 0 < new_paid_amount < invoice.total_amount:
            status = InvoiceStatus.PARTIALLY_PAID
            fully_paid_date = invoice.fully_paid_date
            paid_amount = new_paid_amount
        else:
            # If payment amount is zero or negative, no change to the invoice status
            paid_amount = invoice.paid_amount
            status = invoice.status
            fully_paid_date = invoice.fully_paid_date

        # Update the invoice in the database
        self.db.execute(
            update(Invoice)
            .where(Invoice.id == invoice_id)
            .values(
                paid_amount=paid_amount, status=status, fully_paid_date=fully_paid_date
            )
        )
        self.db.commit()

        # Refresh and return the updated invoice
        updated_invoice = self.get_invoice(invoice_id)
        return updated_invoice

    # Payment Operations
    def create_payment(
        self,
        owner_id: int,
        client_id: int,
        invoice_id: int,
        amount: float,
        payment_method: PaymentMethod,
        payment_date: datetime,
        description: Optional[str] = None,
    ) -> Payment:
        payment = Payment(
            owner_id=owner_id,
            client_id=client_id,
            invoice_id=invoice_id,
            status=PaymentStatus.PENDING,
            amount=amount,
            payment_method=payment_method,
            payment_date=payment_date,
            description=description,
        )
        self.db.add(payment)
        self.db.flush()

        invoice = self.get_invoice(invoice_id)
        invoice = self.add_payment_to_invoice(invoice_id, amount)

        # Update payment status to completed
        self.db.query(Payment).filter(Payment.id == payment.id).update(
            {"status": PaymentStatus.COMPLETED}
        )
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment(self, payment_id: int) -> Payment:
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
            )
        return payment

    def update_payment(self, payment_id: int, **kwargs) -> Payment:
        payment = self.get_payment(payment_id)
        for key, value in kwargs.items():
            if hasattr(payment, key):
                setattr(payment, key, value)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def delete_payment(self, payment_id: int) -> None:
        payment = self.get_payment(payment_id)
        self.db.delete(payment)
        self.db.commit()
