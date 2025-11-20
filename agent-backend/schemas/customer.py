# backend/schemas/customer.py
from pydantic import BaseModel, EmailStr
from datetime import datetime


class CustomerBase(BaseModel):
    full_name: str
    email: EmailStr
    title: str | None = None
    location: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
