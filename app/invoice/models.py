import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    Float,
    Boolean,
    Enum,
    ForeignKey,
    func,
    Sequence,
    event,
)
from sqlalchemy.orm import relationship

from app.database import Base

# Create a sequence for generating the reference number
invoice_seq = Sequence("invoice_seq", start=1, increment=1)
payment_seq = Sequence("payment_seq", start=1, increment=1)
client_seq = Sequence("client_seq", start=1, increment=1)


class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    VOIDED = "voided"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentMethod(enum.Enum):
    BANK = "bank"
    CARD = "card"
    CASH = "cash"


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    reference = Column(String(50), unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    owner = relationship("User", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client")
    payments = relationship("Payment", back_populates="client")

    @staticmethod
    def generate_reference(context):
        next_value = context.connection.execute(client_seq)
        return f"CLI{next_value}"


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    owner = relationship("User", back_populates="items")
    invoice_items = relationship("InvoiceItem", back_populates="item")


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    reference = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(InvoiceStatus), nullable=False)
    issuing_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    fully_paid_date = Column(DateTime, nullable=True)
    total_amount = Column(Float)
    paid_amount = Column(Float, default=0)
    currency = Column(String, default="USD")
    is_sent = Column(Boolean, default=False)
    sent_times = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    owner = relationship("User", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    invoice_items = relationship("InvoiceItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")

    @staticmethod
    def generate_reference(context):
        next_value = context.connection.execute(invoice_seq)
        return f"INV{next_value}"


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    item_amount = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    invoice = relationship("Invoice", back_populates="invoice_items")
    item = relationship("Item", back_populates="invoice_items")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    reference = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False)
    description = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH)
    payment_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    owner = relationship("User", back_populates="payments")
    client = relationship("Client", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")

    @staticmethod
    def generate_reference(context):
        next_value = context.connection.execute(payment_seq)
        return f"PY{next_value}"


# Event listener for before_insert to handle automatic generation
@event.listens_for(Invoice, "before_insert")
def before_insert_invoice_listener(mapper, connection, target):
    if not target.reference:  # Only generate if the reference is not manually provided
        target.reference = Invoice.generate_reference(connection)


@event.listens_for(Payment, "before_insert")
def before_insert_payment_listener(mapper, connection, target):
    if not target.reference:
        target.reference = Payment.generate_reference(connection)


@event.listens_for(Client, "before_insert")
def before_insert_client_listener(mapper, connection, target):
    if not target.reference:
        target.reference = Client.generate_reference(connection)
