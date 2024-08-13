from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional

from app.invoicing.schemas import ClientInDB, ItemInDB, InvoiceInDB, PaymentInDB


class UserBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: EmailStr
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDB(UserBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    clients: List[ClientInDB] = []
    items: List[ItemInDB] = []
    invoices: List[InvoiceInDB] = []
    payments: List[PaymentInDB] = []

    class Config:
        from_attributes = True
