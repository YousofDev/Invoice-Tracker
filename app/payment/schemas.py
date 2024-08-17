import enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentMethod(enum.Enum):
    CASH = "cash"
    BANK = "bank"
    CARD = "card"


class PaymentBase(BaseModel):
    status: Optional[PaymentStatus] = PaymentStatus.COMPLETED
    payment_method: Optional[PaymentMethod] = PaymentMethod.CASH
    description: Optional[str] = None
    amount: float
    currency: Optional[str] = "USD"


class PaymentCreate(PaymentBase):
    owner_id: int
    client_id: int
    invoice_id: int
    payment_date: Optional[datetime] = datetime.now()


class PaymentUpdate(PaymentBase):
    pass


class PaymentInDB(PaymentBase):
    id: int
    owner_id: int
    client_id: int
    invoice_id: int
    payment_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
