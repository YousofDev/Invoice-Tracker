from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Invoice(Base):
    pass


class Item(Base):
    pass


class InvoiceItem(Base):
    pass


class Client(Base):
    pass


class Payment(Base):
    pass


class InvoicePayment(Base):
    pass
