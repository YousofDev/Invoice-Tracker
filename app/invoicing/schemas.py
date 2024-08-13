import enum
from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional
from datetime import datetime


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
    CASH = "cash"
    BANK = "bank"
    CARD = "card"


# Client Schema:
class ClientBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True


class ClientCreate(ClientBase):
    owner_id: int
    reference: Optional[str] = None


class ClientUpdate(ClientBase):
    pass


class ClientInDB(ClientBase):
    id: int
    created_at: Optional[str]
    updated_at: Optional[str]
    owner_id: int
    reference: str

    class Config:
        from_attributes = True


# Item Schema:
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_active: Optional[bool] = True


class ItemCreate(ItemBase):
    owner_id: int


class ItemUpdate(ItemBase):
    pass


class ItemInDB(ItemBase):
    id: int
    owner_id: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


# Invoice Schema:
class InvoiceBase(BaseModel):
    status: InvoiceStatus
    issuing_date: datetime
    due_date: datetime
    fully_paid_date: Optional[datetime] = None
    total_amount: float
    paid_amount: Optional[float] = 0
    currency: Optional[str] = "USD"
    is_sent: Optional[bool] = False
    sent_times: Optional[int] = 0


class InvoiceCreate(InvoiceBase):
    client_id: int
    owner_id: int
    reference: Optional[str] = None


class InvoiceUpdate(InvoiceBase):
    pass


class InvoiceInDB(InvoiceBase):
    id: int
    client_id: int
    owner_id: int
    reference: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class InvoiceItemBase(BaseModel):
    invoice_id: int
    item_id: int
    quantity: int
    price: float
    item_amount: Optional[float] = None


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemUpdate(InvoiceItemBase):
    pass


class InvoiceItemInDB(InvoiceItemBase):
    id: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


# Payment Schema:
class PaymentBase(BaseModel):
    client_id: Optional[int]
    invoice_id: Optional[int]
    status: PaymentStatus
    description: Optional[str] = None
    amount: float
    currency: Optional[str] = "USD"
    payment_method: Optional[PaymentMethod] = PaymentMethod.CASH
    payment_date: datetime


class PaymentCreate(PaymentBase):
    owner_id: int
    reference: Optional[str] = None


class PaymentUpdate(PaymentBase):
    pass


class PaymentInDB(PaymentBase):
    id: int
    owner_id: int
    reference: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True
