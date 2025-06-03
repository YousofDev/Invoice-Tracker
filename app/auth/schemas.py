from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


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

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id: int

    class Config:
        from_attributes = True
