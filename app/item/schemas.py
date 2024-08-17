from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
