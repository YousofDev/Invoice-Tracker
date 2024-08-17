from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    Boolean,
    ForeignKey,
    func,
)

from app.database import Base


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    owner = relationship("User", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client")
    payments = relationship("Payment", back_populates="client")
