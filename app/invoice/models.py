from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    Numeric,
    Boolean,
    Enum,
    ForeignKey,
    func,
)

from app.database import Base
from app.invoice.schemas import InvoiceStatus


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.UNPAID)
    description = Column(String, nullable=True)
    issuing_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    fully_paid_date = Column(DateTime, nullable=True)
    total_amount = Column(Numeric)
    paid_amount = Column(Numeric, default=0)
    currency = Column(String, default="USD")
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    owner = relationship("User", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    invoice_items = relationship("InvoiceItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric, nullable=False)
    item_amount = Column(Numeric)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    invoice = relationship(
        "Invoice", back_populates="invoice_items", passive_deletes=True
    )
    item = relationship("Item", back_populates="invoice_items")
