from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ClientBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True


class ClientCreate(ClientBase):
    owner_id: int


class ClientUpdate(ClientBase):
    pass


class ClientInDB(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        from_attributes = True
