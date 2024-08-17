from decimal import Decimal
from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, update
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.invoice.models import Invoice
from app.payment.models import Payment
from app.invoice.schemas import InvoiceStatus
from app.payment.schemas import (
    PaymentCreate,
    PaymentUpdate,
    PaymentInDB,
)


class PaymentService:

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_payment_list(self, skip: int = 0, limit: int = 100):
        return self.db.query(Payment).offset(skip).limit(limit).all()

    def get_payment(self, payment_id: int) -> PaymentInDB:
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
            )

        return PaymentInDB.model_validate(payment)

    def create_payment(self, payment_data: PaymentCreate) -> PaymentInDB:
        payment_dict = payment_data.model_dump()

        # Retrieve the invoice
        invoice = (
            self.db.query(Invoice)
            .filter(Invoice.id == payment_dict["invoice_id"])
            .one_or_none()
        )

        if invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found.")

        if invoice.status is InvoiceStatus.PAID:
            raise HTTPException(
                status_code=400, detail="Invoice is already fully paid."
            )

        remaining_amount = invoice.total_amount - invoice.paid_amount

        if payment_dict["amount"] > remaining_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Payment amount {payment_dict["amount"]} should not exceeds the unpaid amount {remaining_amount}',
            )

        payment = Payment(**payment_dict)
        self.db.add(payment)

        new_paid_amount = Decimal(str(invoice.paid_amount)) + Decimal(
            str(payment.amount)
        )

        # Update invoice
        self.db.execute(
            update(Invoice)
            .where(Invoice.id == invoice.id)
            .values(paid_amount=new_paid_amount)
        )

        invoice.payments.append(payment)

        # Check if invoice is fully paid
        fully_paid_check = (
            self.db.query(Invoice.paid_amount == invoice.total_amount)
            .filter(Invoice.id == invoice.id)
            .scalar()
        )

        if fully_paid_check:
            self.db.execute(
                update(Invoice)
                .where(Invoice.id == invoice.id)
                .values(
                    status=InvoiceStatus.PAID,
                    fully_paid_date=payment_dict["payment_date"] or datetime.now(),
                )
            )

        self.db.commit()
        self.db.refresh(payment)

        return PaymentInDB.model_validate(payment)

    def update_payment(
        self, payment_id: int, payment_data: PaymentUpdate
    ) -> PaymentInDB:
        payment_dict = payment_data.model_dump()

        # Retrieve the payment to be updated
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()

        if payment is None:
            raise HTTPException(status_code=404, detail="Payment not found.")

        # Retrieve the invoice
        invoice = (
            self.db.query(Invoice)
            .filter(Invoice.id == payment.invoice_id)
            .one_or_none()
        )

        if invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found.")

        # Calculate the new total payments amount
        new_total_payments_amount = (
            Decimal(str(invoice.paid_amount))
            - Decimal(str(payment.amount))
            + Decimal(str(payment_dict["amount"]))
        )

        # Check if the new total payments amount exceeds the invoice total amount
        if new_total_payments_amount > Decimal(str(invoice.total_amount)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"New total payments amount {new_total_payments_amount} should not exceed the invoice total amount {invoice.total_amount}",
            )

        # Update the payment
        payment.amount = payment_dict["amount"]

        self.db.add(payment)

        # Update the invoice paid amount
        self.db.execute(
            update(Invoice)
            .where(Invoice.id == invoice.id)
            .values(paid_amount=new_total_payments_amount)
        )

        # Check if invoice is fully paid and update status and fully paid date
        if new_total_payments_amount == invoice.total_amount:
            self.db.execute(
                update(Invoice)
                .where(Invoice.id == invoice.id)
                .values(
                    status=InvoiceStatus.PAID,
                    fully_paid_date=datetime.now(),
                )
            )
        else:
            self.db.execute(
                update(Invoice)
                .where(Invoice.id == invoice.id)
                .values(status=InvoiceStatus.PARTIALLY_PAID)
            )

        self.db.commit()

        self.db.refresh(payment)

        return PaymentInDB.model_validate(payment)

    def delete_payment(self, payment_id: int) -> None:

        # Retrieve the payment to be updated
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()

        if payment is None:
            raise HTTPException(status_code=404, detail="Payment not found.")

        # Retrieve the invoice
        invoice = (
            self.db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
        )

        if invoice is not None:
            # Calculate the new total payments amount
            new_paid_amount = Decimal(str(invoice.paid_amount)) - Decimal(
                str(payment.amount)
            )

            # Update the invoice status and paid amount
            self.db.execute(
                update(Invoice)
                .where(Invoice.id == invoice.id)
                .values(
                    paid_amount=new_paid_amount, status=InvoiceStatus.PARTIALLY_PAID
                )
            )

        self.db.execute(delete(Payment).where(Payment.id == payment_id))

        self.db.commit()

    def find_payment(self, id: int) -> Payment:
        resource = self.db.query(Payment).filter(Payment.id == id).first()
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
            )
        return resource
