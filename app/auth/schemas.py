from datetime import datetime
from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional

from app.client.schemas import ClientInDB
from app.invoice.schemas import InvoiceInDB
from app.item.schemas import ItemInDB
from app.payment.schemas import PaymentInDB


class UserBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: EmailStr
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    clients: List[ClientInDB] = []
    items: List[ItemInDB] = []
    invoices: List[InvoiceInDB] = []
    payments: List[PaymentInDB] = []

    class Config:
        from_attributes = True
