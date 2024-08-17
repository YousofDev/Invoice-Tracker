from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    Numeric,
    Enum,
    ForeignKey,
    func,
)

from app.database import Base
from app.payment.schemas import PaymentStatus, PaymentMethod


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"))
    status = Column(Enum(PaymentStatus), default=PaymentStatus.COMPLETED)
    description = Column(String, nullable=True)
    amount = Column(Numeric, nullable=False)
    currency = Column(String, default="USD")
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH)
    payment_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    owner = relationship("User", back_populates="payments")
    client = relationship("Client", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments", passive_deletes=True)
