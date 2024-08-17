from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    Numeric,
    Boolean,
    ForeignKey,
    func,
)

from app.database import Base


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    owner = relationship("User", back_populates="items")
    invoice_items = relationship("InvoiceItem", back_populates="item")
