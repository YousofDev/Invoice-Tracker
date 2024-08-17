import enum
from pydantic import BaseModel, computed_field
from typing import Optional
from datetime import datetime


class InvoiceStatus(enum.Enum):
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"


class InvoiceItemBase(BaseModel):
    item_id: int
    quantity: int
    price: float

    @computed_field
    def item_amount(self) -> float:
        return float(self.quantity) * float(self.price)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemUpdate(InvoiceItemBase):
    pass


class InvoiceItemInDB(InvoiceItemBase):
    id: int
    invoice_id: int
    item_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    status: Optional[InvoiceStatus] = InvoiceStatus.UNPAID
    currency: Optional[str] = "USD"
    is_sent: Optional[bool] = False


class InvoiceCreate(InvoiceBase):
    client_id: int
    owner_id: int
    issuing_date: Optional[datetime] = datetime.now()
    due_date: Optional[datetime] = datetime.now()
    items: list[InvoiceItemCreate]


class InvoiceUpdate(InvoiceBase):
    items: list[InvoiceItemUpdate]


class InvoiceInDB(InvoiceBase):
    id: int
    client_id: int
    owner_id: int
    total_amount: Optional[float] = 0
    paid_amount: Optional[float] = 0
    issuing_date: datetime
    due_date: datetime
    fully_paid_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: list[InvoiceItemInDB]

    class Config:
        from_attributes = True
